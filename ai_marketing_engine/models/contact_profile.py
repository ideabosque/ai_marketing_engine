#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

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
from silvaengine_utility import Utility

from ..types.contact_profile import ContactProfileListType, ContactProfileType
from .utils import _get_attribute_values, _get_place, _insert_update_attribute_values


class EmailIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "email-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    place_uuid = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute(range_key=True)


class ContactProfileModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-contact_profiles"

    place_uuid = UnicodeAttribute(hash_key=True)
    contact_uuid = UnicodeAttribute(range_key=True)
    email = UnicodeAttribute()
    endpoint_id = UnicodeAttribute()
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    email_index = EmailIndex()


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
def get_contact_profile(place_uuid: str, contact_uuid: str) -> ContactProfileModel:
    return ContactProfileModel.get(place_uuid, contact_uuid)


def get_contact_profile_count(place_uuid: str, contact_uuid: str) -> int:
    return ContactProfileModel.count(
        place_uuid, ContactProfileModel.contact_uuid == contact_uuid
    )


def get_contact_profile_type(
    info: ResolveInfo, contact_profile: ContactProfileModel
) -> ContactProfileType:
    try:
        place = _get_place(contact_profile.endpoint_id, contact_profile.place_uuid)
        data = _get_attribute_values(
            contact_profile.endpoint_id, contact_profile.contact_uuid, "contact"
        )
        contact_profile = contact_profile.__dict__["attribute_values"]
        contact_profile["place"] = place
        contact_profile.pop("place_uuid")
        contact_profile["data"] = data

    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e

    return ContactProfileType(**Utility.json_loads(Utility.json_dumps(contact_profile)))


def resolve_contact_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactProfileType:
    return get_contact_profile_type(
        info,
        get_contact_profile(kwargs.get("place_uuid"), kwargs.get("contact_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["place_uuid", "contact_uuid", "email"],
    list_type_class=ContactProfileListType,
    type_funct=get_contact_profile_type,
)
def resolve_contact_profile_list(info: ResolveInfo, **kwargs: Dict[str, Any]) -> Any:
    place_uuid = kwargs.get("place_uuid")
    email = kwargs.get("email")
    first_name = kwargs.get("first_name")
    last_name = kwargs.get("last_name")

    args = []
    inquiry_funct = ContactProfileModel.scan
    count_funct = ContactProfileModel.count
    if place_uuid:
        args = [place_uuid, None]
        inquiry_funct = ContactProfileModel.query
        if email:
            count_funct = ContactProfileModel.email_index.count
            args[1] = ContactProfileModel.email == email
            inquiry_funct = ContactProfileModel.email_index.query

    the_filters = None  # We can add filters for the query.
    if first_name:
        the_filters &= ContactProfileModel.first_name.contains(first_name)
    if last_name:
        the_filters &= ContactProfileModel.last_name.contains(last_name)
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "place_uuid",
        "range_key": "contact_uuid",
    },
    model_funct=get_contact_profile,
    count_funct=get_contact_profile_count,
    type_funct=get_contact_profile_type,
)
def insert_update_contact_profile(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    place_uuid = kwargs.get("place_uuid")
    contact_uuid = kwargs.get("contact_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "email": kwargs["email"],
            "endpoint_id": info.context["endpoint_id"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        for key in [
            "first_name",
            "last_name",
            "corporation_uuid",
        ]:
            if key in kwargs:
                cols[key] = kwargs[key]
        ContactProfileModel(
            place_uuid,
            contact_uuid,
            **cols,
        ).save()
        return

    contact_profile = kwargs.get("entity")
    actions = [
        ContactProfileModel.updated_by.set(kwargs["updated_by"]),
        ContactProfileModel.updated_at.set(pendulum.now("UTC")),
    ]

    # Map of kwargs keys to ContactProfileModel attributes
    field_map = {
        "email": ContactProfileModel.email,
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


@delete_decorator(
    keys={
        "hash_key": "place_uuid",
        "range_key": "contact_uuid",
    },
    model_funct=get_contact_profile,
)
def delete_contact_profile(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True
