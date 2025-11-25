#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import functools
import logging
import traceback
from typing import Any, Dict

import pendulum
from graphene import ResolveInfo
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.indexes import AllProjection, LocalSecondaryIndex
from tenacity import retry, stop_after_attempt, wait_exponential

from silvaengine_dynamodb_base import (
    BaseModel,
    delete_decorator,
    insert_update_decorator,
    monitor_decorator,
    resolve_list_decorator,
)
from silvaengine_utility import Utility, method_cache

from ..handlers.config import Config

from ..handlers.ai_marketing_utility import data_sync_decorator
from ..types.contact_profile import ContactProfileListType, ContactProfileType
from .utils import _insert_update_attribute_values


class EmailIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "email-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    endpoint_id = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute(range_key=True)


class PlaceUuidIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "place_uuid-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    endpoint_id = UnicodeAttribute(hash_key=True)
    place_uuid = UnicodeAttribute(range_key=True)


class ContactProfileModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-contact_profiles"

    endpoint_id = UnicodeAttribute(hash_key=True)
    contact_uuid = UnicodeAttribute(range_key=True)
    email = UnicodeAttribute()
    place_uuid = UnicodeAttribute()
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    email_index = EmailIndex()
    place_uuid_index = PlaceUuidIndex()


def purge_cache():
    def actual_decorator(original_function):
        @functools.wraps(original_function)
        def wrapper_function(*args, **kwargs):
            try:
                from ..models.cache import purge_entity_cascading_cache

                endpoint_id = args[0].context.get("endpoint_id") or kwargs.get(
                    "endpoint_id"
                )
                entity_keys = {}
                if kwargs.get("contact_uuid"):
                    entity_keys["contact_uuid"] = kwargs.get("contact_uuid")

                result = purge_entity_cascading_cache(
                    args[0].context.get("logger"),
                    entity_type="contact_profile",
                    context_keys={"endpoint_id": endpoint_id} if endpoint_id else None,
                    entity_keys=entity_keys if entity_keys else None,
                    cascade_depth=3,
                )

                result = original_function(*args, **kwargs)
                return result
            except Exception as e:
                log = traceback.format_exc()
                args[0].context.get("logger").error(log)
                raise e
        return wrapper_function
    return actual_decorator


def create_contact_profile_table(logger: logging.Logger) -> bool:
    """Create the ContactProfile table if it doesn't exist."""
    if not ContactProfileModel.exists():
        # Create with on-demand billing (PAY_PER_REQUEST)
        ContactProfileModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        logger.info("The ContactProfile table has been created.")
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
@method_cache(
    ttl=Config.get_cache_ttl(), 
    cache_name=Config.get_cache_name("models", "contact_profile")
)
def get_contact_profile(endpoint_id: str, contact_uuid: str) -> ContactProfileModel:
    return ContactProfileModel.get(endpoint_id, contact_uuid)


def get_contact_profile_count(endpoint_id: str, contact_uuid: str) -> int:
    return ContactProfileModel.count(
        endpoint_id, ContactProfileModel.contact_uuid == contact_uuid
    )


def get_contact_profile_type(
    info: ResolveInfo, contact_profile: ContactProfileModel
) -> ContactProfileType:
    """
    Nested resolver approach: return minimal contact_profile data.
    - Do NOT embed 'place'
    - Do NOT embed 'data'
    Those are resolved lazily by ContactProfileType resolvers.
    """
    try:
        cp_dict = contact_profile.__dict__["attribute_values"]
    except Exception:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise

    return ContactProfileType(**Utility.json_normalize(cp_dict))


def resolve_contact_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactProfileType:
    endpoint_id = info.context.get("endpoint_id")
    if kwargs.get("email"):
        existing_profiles = list(
            ContactProfileModel.email_index.query(
                endpoint_id, ContactProfileModel.email == kwargs["email"], limit=1
            )
        )
        if existing_profiles:
            return get_contact_profile_type(info, existing_profiles[0])

    count = get_contact_profile_count(endpoint_id, kwargs.get("contact_uuid"))
    if count == 0:
        return None

    return get_contact_profile_type(
        info,
        get_contact_profile(endpoint_id, kwargs.get("contact_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "contact_uuid", "email", "place_uuid"],
    list_type_class=ContactProfileListType,
    type_funct=get_contact_profile_type,
)
def resolve_contact_profile_list(info: ResolveInfo, **kwargs: Dict[str, Any]) -> Any:
    place_uuid = kwargs.get("place_uuid")
    email = kwargs.get("email")
    first_name = kwargs.get("first_name")
    last_name = kwargs.get("last_name")
    endpoint_id = info.context.get("endpoint_id", None)

    args = []
    inquiry_funct = ContactProfileModel.scan
    count_funct = ContactProfileModel.count

    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = ContactProfileModel.query

        if place_uuid:
            # Use place_uuid_index to query by place_uuid
            inquiry_funct = ContactProfileModel.place_uuid_index.query
            args[1] = ContactProfileModel.place_uuid == place_uuid
            count_funct = ContactProfileModel.place_uuid_index.count
        if email:
            # Use email_index to query by email
            inquiry_funct = ContactProfileModel.email_index.query
            args[1] = ContactProfileModel.email == email
            count_funct = ContactProfileModel.email_index.count

    the_filters = None  # We can add filters for the query.
    if first_name:
        the_filters &= ContactProfileModel.first_name.contains(first_name)
    if last_name:
        the_filters &= ContactProfileModel.last_name.contains(last_name)
    if place_uuid and email:
        # If both place_uuid and email are specified, add place_uuid as a filter
        the_filters &= ContactProfileModel.place_uuid == place_uuid
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@purge_cache()
@data_sync_decorator
@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "contact_uuid",
    },
    model_funct=get_contact_profile,
    count_funct=get_contact_profile_count,
    type_funct=get_contact_profile_type,
)
def insert_update_contact_profile(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    contact_uuid = kwargs.get("contact_uuid")
    if kwargs.get("entity") is None:
        # Check if email already exists
        email = kwargs["email"]
        existing_profiles = list(
            ContactProfileModel.email_index.query(
                endpoint_id, ContactProfileModel.email == email, limit=1
            )
        )
        if existing_profiles:
            raise ValueError(
                f"Contact profile with email '{email}' already exists for contact_uuid: "
                f"{existing_profiles[0].contact_uuid}"
            )

        cols = {
            "email": email,
            "place_uuid": kwargs["place_uuid"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        for key in [
            "first_name",
            "last_name",
        ]:
            if key in kwargs:
                cols[key] = kwargs[key]
        ContactProfileModel(
            endpoint_id,
            contact_uuid,
            **cols,
        ).save()

        data = _insert_update_attribute_values(
            info, "contact", contact_uuid, kwargs["updated_by"], kwargs.get("data", {})
        )
        info.context["logger"].info(f"Contact profile data: {data} has been updated.")

        return

    contact_profile = kwargs.get("entity")
    actions = [
        ContactProfileModel.updated_by.set(kwargs["updated_by"]),
        ContactProfileModel.updated_at.set(pendulum.now("UTC")),
    ]

    # Map of kwargs keys to ContactProfileModel attributes
    field_map = {
        "email": ContactProfileModel.email,
        "place_uuid": ContactProfileModel.place_uuid,
        "first_name": ContactProfileModel.first_name,
        "last_name": ContactProfileModel.last_name,
    }

    # Add actions dynamically based on the presence of keys in kwargs
    for key, field in field_map.items():
        if key in kwargs:  # Check if the key exists in kwargs
            actions.append(field.set(None if kwargs[key] == "null" else kwargs[key]))

    # Update the contact profile
    contact_profile.update(actions=actions)

    data = _insert_update_attribute_values(
        info, "contact", contact_uuid, kwargs["updated_by"], kwargs.get("data", {})
    )
    info.context["logger"].info(f"Contact profile data: {data} has been updated.")

    return


@purge_cache()
@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "contact_uuid",
    },
    model_funct=get_contact_profile,
)
def delete_contact_profile(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True
