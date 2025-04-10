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

from ..types.contact_request import ContactRequestListType, ContactRequestType
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
    contact_uuid = UnicodeAttribute(hash_key=True)
    place_uuid = UnicodeAttribute(range_key=True)


class ContactRequestModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-contact_requests"

    contact_uuid = UnicodeAttribute(hash_key=True)
    request_uuid = UnicodeAttribute(range_key=True)
    place_uuid = UnicodeAttribute()
    endpoint_id = UnicodeAttribute()
    request_title = UnicodeAttribute()
    request_detail = UnicodeAttribute()
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    place_uuid_index = PlaceUuidIndex()


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
def get_contact_request(contact_uuid: str, request_uuid: str) -> ContactRequestModel:
    return ContactRequestModel.get(contact_uuid, request_uuid)


def get_contact_request_count(contact_uuid: str, request_uuid: str) -> int:
    return ContactRequestModel.count(
        contact_uuid, ContactRequestModel.request_uuid == request_uuid
    )


def get_contact_request_type(
    info: ResolveInfo, contact_request: ContactRequestModel
) -> ContactRequestType:
    try:
        contact_profile = _get_contact_profile(
            contact_request.place_uuid, contact_request.contact_uuid
        )
        contact_request = contact_request.__dict__["attribute_values"]
        contact_request["contact_profile"] = contact_profile
        contact_request.pop("place_uuid")
        contact_request.pop("contact_uuid")
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    return ContactRequestType(**Utility.json_loads(Utility.json_dumps(contact_request)))


def resolve_contact_request(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactRequestType:
    return get_contact_request_type(
        info,
        get_contact_request(kwargs.get("contact_uuid"), kwargs.get("request_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["contact_uuid", "request_uuid", "place_uuid"],
    list_type_class=ContactRequestListType,
    type_funct=get_contact_request_type,
)
def resolve_contact_request_list(info: ResolveInfo, **kwargs: Dict[str, Any]) -> Any:
    contact_uuid = kwargs.get("contact_uuid")
    endpoint_id = info.context["endpoint_id"]
    request_title = kwargs.get("request_title")
    request_detail = kwargs.get("request_detail")
    place_uuid = kwargs.get("place_uuid")

    args = []
    inquiry_funct = ContactRequestModel.scan
    count_funct = ContactRequestModel.count
    if contact_uuid and place_uuid:
        args = [contact_uuid]
        inquiry_funct = ContactRequestModel.place_uuid_index.query
        if place_uuid:
            count_funct = ContactRequestModel.place_uuid_index.count
            args[1] = ContactRequestModel.place_uuid == place_uuid
            inquiry_funct = ContactRequestModel.place_uuid_index.query

    the_filters = None
    if request_title:
        the_filters &= ContactRequestModel.request_title.contains(request_title)
    if request_detail:
        the_filters &= ContactRequestModel.request_detail.contains(request_detail)
    if endpoint_id:
        the_filters &= ContactRequestModel.endpoint_id == endpoint_id
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "contact_uuid",
        "range_key": "request_uuid",
    },
    model_funct=get_contact_request,
    count_funct=get_contact_request_count,
    type_funct=get_contact_request_type,
)
def insert_update_contact_request(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    contact_uuid = kwargs.get("contact_uuid")
    request_uuid = kwargs.get("request_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "endpoint_id": kwargs["endpoint_id"],
            "request_title": kwargs["request_title"],
            "request_detail": kwargs["request_detail"],
            "place_uuid": kwargs["place_uuid"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        ContactRequestModel(
            contact_uuid,
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


@delete_decorator(
    keys={
        "hash_key": "contact_uuid",
        "range_key": "request_uuid",
    },
    model_funct=get_contact_request,
)
def delete_contact_request(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True
