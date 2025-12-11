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
from silvaengine_dynamodb_base import (
    BaseModel,
    delete_decorator,
    insert_update_decorator,
    monitor_decorator,
    resolve_list_decorator,
)
from silvaengine_utility import Utility, method_cache

from ..handlers.config import Config
from tenacity import retry, stop_after_attempt, wait_exponential

from ..types.contact_request import ContactRequestListType, ContactRequestType
from .contact_profile import get_contact_profile_count
from .utils import _get_contact_profile


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


class ContactUuidIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "contact_uuid-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    endpoint_id = UnicodeAttribute(hash_key=True)
    contact_uuid = UnicodeAttribute(range_key=True)


class ContactRequestModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-contact_requests"

    endpoint_id = UnicodeAttribute(hash_key=True)
    request_uuid = UnicodeAttribute(range_key=True)
    contact_uuid = UnicodeAttribute()
    place_uuid = UnicodeAttribute()
    request_title = UnicodeAttribute()
    request_detail = UnicodeAttribute()
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    place_uuid_index = PlaceUuidIndex()
    contact_uuid_index = ContactUuidIndex()


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
                if kwargs.get("request_uuid"):
                    entity_keys["request_uuid"] = kwargs.get("request_uuid")

                result = purge_entity_cascading_cache(
                    args[0].context.get("logger"),
                    entity_type="contact_request",
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


def create_contact_request_table(logger: logging.Logger) -> bool:
    """Create the ContactRequest table if it doesn't exist."""
    if not ContactRequestModel.exists():
        # Create with on-demand billing (PAY_PER_REQUEST)
        ContactRequestModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        logger.info("The ContactRequest table has been created.")
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
@method_cache(
    ttl=Config.get_cache_ttl(), 
    cache_name=Config.get_cache_name("models", "contact_request")
)
def get_contact_request(endpoint_id: str, request_uuid: str) -> ContactRequestModel:
    return ContactRequestModel.get(endpoint_id, request_uuid)


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def _get_contact_request(endpoint_id: str, request_uuid: str) -> ContactRequestModel:
    return ContactRequestModel.get(endpoint_id, request_uuid)


def get_contact_request_count(endpoint_id: str, request_uuid: str) -> int:
    return ContactRequestModel.count(
        endpoint_id, ContactRequestModel.request_uuid == request_uuid
    )


def get_contact_request_type(
    info: ResolveInfo, contact_request: ContactRequestModel
) -> ContactRequestType:
    """
    Nested resolver approach: return minimal contact_request data.
    - Do NOT embed 'contact_profile'
    That is resolved lazily by ContactRequestType.resolve_contact_profile.
    """
    try:
        contact_profile = _get_contact_profile(
            contact_request.endpoint_id, contact_request.contact_uuid
        )
        contact_request = contact_request.__dict__["attribute_values"]
        contact_request["contact_profile"] = contact_profile
        contact_request.pop("place_uuid")
        contact_request.pop("contact_uuid")
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    return ContactRequestType(**Utility.json_normalize(contact_request))


def resolve_contact_request(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactRequestType | None:
    endpoint_id = info.context["endpoint_id"]
    count = get_contact_request_count(endpoint_id, kwargs.get("request_uuid"))
    if count == 0:
        return None

    return get_contact_request_type(
        info,
        get_contact_request(endpoint_id, kwargs.get("request_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "contact_uuid", "request_uuid", "place_uuid"],
    list_type_class=ContactRequestListType,
    type_funct=get_contact_request_type,
)
def resolve_contact_request_list(info: ResolveInfo, **kwargs: Dict[str, Any]) -> Any:
    endpoint_id = info.context["endpoint_id"]
    contact_uuid = kwargs.get("contact_uuid")
    request_title = kwargs.get("request_title")
    request_detail = kwargs.get("request_detail")
    place_uuid = kwargs.get("place_uuid")

    args = []
    inquiry_funct = ContactRequestModel.scan
    count_funct = ContactRequestModel.count

    # Use place_uuid_index if both endpoint_id and place_uuid are provided
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = ContactRequestModel.query
        if place_uuid:
            inquiry_funct = ContactRequestModel.place_uuid_index.query
            args[1] = ContactRequestModel.place_uuid == place_uuid
            count_funct = ContactRequestModel.place_uuid_index.count
        if contact_uuid:
            inquiry_funct = ContactRequestModel.contact_uuid_index.query
            args[1] = ContactRequestModel.contact_uuid == contact_uuid
            count_funct = ContactRequestModel.contact_uuid_index.count

    the_filters = None
    if place_uuid and contact_uuid:
        the_filters &= ContactRequestModel.place_uuid == place_uuid
    if request_title:
        the_filters &= ContactRequestModel.request_title.contains(request_title)
    if request_detail:
        the_filters &= ContactRequestModel.request_detail.contains(request_detail)
    if place_uuid and contact_uuid:
        # If both place_uuid and contact_uuid are specified, add place_uuid as a filter
        the_filters &= ContactRequestModel.place_uuid == place_uuid
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@purge_cache()
@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "request_uuid",
    },
    model_funct=_get_contact_request,
    count_funct=get_contact_request_count,
    type_funct=get_contact_request_type,
)
def insert_update_contact_request(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    request_uuid = kwargs.get("request_uuid")

    assert (
        get_contact_profile_count(
            endpoint_id=endpoint_id, contact_uuid=kwargs["contact_uuid"]
        )
        == 1
    ), "Contact profile not found."

    if kwargs.get("entity") is None:
        cols = {
            "contact_uuid": kwargs["contact_uuid"],
            "place_uuid": kwargs["place_uuid"],
            "request_title": kwargs["request_title"],
            "request_detail": kwargs["request_detail"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        ContactRequestModel(
            endpoint_id,
            request_uuid,
            **cols,
        ).save()
        return

    contact_request = kwargs.get("entity")
    actions = [
        ContactRequestModel.updated_by.set(kwargs["updated_by"]),
        ContactRequestModel.updated_at.set(pendulum.now("UTC")),
    ]
    if kwargs.get("request_title") is not None:
        actions.append(ContactRequestModel.request_title.set(kwargs["request_title"]))
    if kwargs.get("request_detail") is not None:
        actions.append(ContactRequestModel.request_detail.set(kwargs["request_detail"]))
    if kwargs.get("place_uuid") is not None:
        actions.append(ContactRequestModel.place_uuid.set(kwargs["place_uuid"]))

    contact_request.update(actions=actions)
    return


@purge_cache()
@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "request_uuid",
    },
    model_funct=get_contact_request,
)
def delete_contact_request(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True
