#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
import traceback
from typing import Any, Dict

import pendulum
from graphene import ResolveInfo
from pynamodb.attributes import ListAttribute, UnicodeAttribute, UTCDateTimeAttribute
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

from ..types.place import PlaceListType, PlaceType
from .utils import _get_corporation_profile


class RegionIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "region-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    place_uuid = UnicodeAttribute(hash_key=True)
    region = UnicodeAttribute(range_key=True)


class PlaceModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-places"

    endpoint_id = UnicodeAttribute(hash_key=True)
    place_uuid = UnicodeAttribute(range_key=True)
    region = UnicodeAttribute()
    latitude = UnicodeAttribute()
    longitude = UnicodeAttribute()
    business_name = UnicodeAttribute()
    address = UnicodeAttribute()
    phone_number = UnicodeAttribute(null=True)
    website = UnicodeAttribute(null=True)
    types = ListAttribute(of=UnicodeAttribute, null=True)
    corporation_uuid = UnicodeAttribute(null=True)
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    region_index = RegionIndex()


def create_place_table(logger: logging.Logger) -> bool:
    """Create the Place table if it doesn't exist."""
    if not PlaceModel.exists():
        # Create with on-demand billing (PAY_PER_REQUEST)
        PlaceModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        logger.info("The Place table has been created.")
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_place(endpoint_id: str, place_uuid: str) -> PlaceModel:
    return PlaceModel.get(endpoint_id, place_uuid)


def get_place_count(endpoint_id: str, place_uuid: str) -> int:
    return PlaceModel.count(endpoint_id, PlaceModel.place_uuid == place_uuid)


def get_place_type(info: ResolveInfo, place: PlaceModel) -> PlaceType:
    place = place.__dict__["attribute_values"]
    try:
        corporation_profile = None
        if place.corporation_uuid:
            corporation_profile = _get_corporation_profile(
                place.endpoint_id,
                place.corporation_uuid,
            )
        place = place.__dict__["attribute_values"]
        if corporation_profile:
            place["corporation_profile"] = corporation_profile
            place.pop("corporation_uuid")

    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e

    return PlaceType(**Utility.json_loads(Utility.json_dumps(place)))


def resolve_place(info: ResolveInfo, **kwargs: Dict[str, Any]) -> PlaceType:
    return get_place_type(
        info,
        get_place(info.context["endpoint_id"], kwargs.get("place_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "place_uuid", "region"],
    list_type_class=PlaceListType,
    type_funct=get_place_type,
)
def resolve_place_list(info: ResolveInfo, **kwargs: Dict[str, Any]) -> Any:
    endpoint_id = info.context["endpoint_id"]
    region = kwargs.get("region")
    latitude = kwargs.get("latitude")
    longitude = kwargs.get("longitude")
    business_name = kwargs.get("business_name")
    address = kwargs.get("address")
    website = kwargs.get("website")
    coorporation_uuid = kwargs.get("corporation_uuid")

    args = []
    inquiry_funct = PlaceModel.scan
    count_funct = PlaceModel.count
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = PlaceModel.query
        if region:
            inquiry_funct = PlaceModel.region_index.query
            args[1] = PlaceModel.region == region
            count_funct = PlaceModel.region_index.count

    the_filters = None  # We can add filters for the query.
    if latitude:
        the_filters &= PlaceModel.latitude == latitude
    if longitude:
        the_filters &= PlaceModel.longitude == longitude
    if business_name:
        the_filters &= PlaceModel.business_name.contains(business_name)
    if address:
        the_filters &= PlaceModel.address.contains(address)
    if website:
        the_filters &= PlaceModel.website.contains(website)
    if coorporation_uuid:
        the_filters &= PlaceModel.corporation_uuid == coorporation_uuid
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "place_uuid",
    },
    model_funct=get_place,
    count_funct=get_place_count,
    type_funct=get_place_type,
)
def insert_update_place(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    place_uuid = kwargs.get("place_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "region": kwargs["region"],
            "latitude": kwargs["latitude"],
            "longitude": kwargs["longitude"],
            "business_name": kwargs["business_name"],
            "address": kwargs["address"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        for key in ["phone_number", "types", "website", "corporation_uuid"]:
            if key in kwargs:
                cols[key] = kwargs[key]
        PlaceModel(
            endpoint_id,
            place_uuid,
            **cols,
        ).save()
        return

    place = kwargs.get("entity")
    actions = [
        PlaceModel.updated_by.set(kwargs["updated_by"]),
        PlaceModel.updated_at.set(pendulum.now("UTC")),
    ]

    # Map of kwargs keys to PlaceModel attributes
    field_map = {
        "region": PlaceModel.region,
        "latitude": PlaceModel.latitude,
        "longitude": PlaceModel.longitude,
        "business_name": PlaceModel.business_name,
        "address": PlaceModel.address,
        "phone_number": PlaceModel.phone_number,
        "website": PlaceModel.website,
        "types": PlaceModel.types,
    }

    # Add actions dynamically based on the presence of keys in kwargs
    for key, field in field_map.items():
        if key in kwargs:  # Check if the key exists in kwargs
            actions.append(field.set(None if kwargs[key] == "null" else kwargs[key]))

    # Handle corporation_uuid separately
    if kwargs.get("corporation_uuid") is not None:
        actions.append(PlaceModel.corporation_uuid.set(kwargs.get("corporation_uuid")))
    elif "corporation_uuid" in kwargs:
        actions.append(PlaceModel.corporation_uuid.remove())

    # Update the place
    place.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "place_uuid",
    },
    model_funct=get_place,
)
def delete_place(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True
