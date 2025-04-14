#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
import traceback
from typing import Any, Dict

import pendulum
from graphene import ResolveInfo
from pynamodb.attributes import (
    ListAttribute,
    MapAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
)
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

from ..types.corporation_profile import (
    CorporationProfileListType,
    CorporationProfileType,
)
from .utils import _get_attribute_values, _insert_update_attribute_values


class CorporationTypeIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "corporation_type-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    endpoint_id = UnicodeAttribute(hash_key=True)
    corporation_type = UnicodeAttribute(range_key=True)


class ExternalIdIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "external_id-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    endpoint_id = UnicodeAttribute(hash_key=True)
    external_id = UnicodeAttribute(range_key=True)


class CorporationProfileModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-corporation_profiles"

    endpoint_id = UnicodeAttribute(hash_key=True)
    corporation_uuid = UnicodeAttribute(range_key=True)
    external_id = UnicodeAttribute()
    corporation_type = UnicodeAttribute()
    business_name = UnicodeAttribute()
    categories = ListAttribute(of=UnicodeAttribute, null=True)
    address = MapAttribute()
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    external_id_index = ExternalIdIndex()
    corporation_type_index = CorporationTypeIndex()


def create_corporation_profile_table(logger: logging.Logger) -> bool:
    """Create the CorporationProfile table if it doesn't exist."""
    if not CorporationProfileModel.exists():
        # Create with on-demand billing (PAY_PER_REQUEST)
        CorporationProfileModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        logger.info("The CorporationProfile table has been created.")
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_corporation_profile(
    endpoint_id: str, corporation_uuid: str
) -> CorporationProfileModel:
    return CorporationProfileModel.get(endpoint_id, corporation_uuid)


def get_corporation_profile_count(endpoint_id: str, corporation_uuid: str) -> int:
    return CorporationProfileModel.count(
        endpoint_id, CorporationProfileModel.corporation_uuid == corporation_uuid
    )


def get_corporation_profile_type(
    info: ResolveInfo, corporation_profile: CorporationProfileModel
) -> CorporationProfileType:
    try:
        data = _get_attribute_values(
            corporation_profile.endpoint_id,
            corporation_profile.corporation_uuid,
            "corporation",
        )
        corporation_profile = corporation_profile.__dict__["attribute_values"]
        corporation_profile["data"] = data
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    return CorporationProfileType(
        **Utility.json_loads(Utility.json_dumps(corporation_profile))
    )


def resolve_corporation_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CorporationProfileType:
    return get_corporation_profile_type(
        info,
        get_corporation_profile(
            info.context["endpoint_id"], kwargs.get("corporation_uuid")
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=[
        "endpoint_id",
        "corporation_uuid",
        "external_id",
        "corporation_type",
    ],
    list_type_class=CorporationProfileListType,
    type_funct=get_corporation_profile_type,
)
def resolve_corporation_profile_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    endpoint_id = info.context["endpoint_id"]
    external_id = kwargs.get("external_id")
    corporation_type = kwargs.get("corporation_type")
    business_name = kwargs.get("business_name")
    category = kwargs.get("category")
    address = kwargs.get("address")

    args = []
    inquiry_funct = CorporationProfileModel.scan
    count_funct = CorporationProfileModel.count
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = CorporationProfileModel.query
        if external_id:
            inquiry_funct = CorporationProfileModel.external_id_index.query
            args[1] = CorporationProfileModel.external_id == external_id
            count_funct = CorporationProfileModel.external_id_index.count
        if corporation_type:
            inquiry_funct = CorporationProfileModel.corporation_type_index.query
            args[1] = CorporationProfileModel.corporation_type == corporation_type
            count_funct = CorporationProfileModel.corporation_type_index.count

    the_filters = None  # We can add filters for the query.
    if business_name:
        the_filters &= CorporationProfileModel.business_name == business_name
    if category:
        the_filters &= CorporationProfileModel.categories.contains(category)
    if address:
        the_filters &= CorporationProfileModel.address.contains(address)
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "corporation_uuid",
    },
    model_funct=get_corporation_profile,
    count_funct=get_corporation_profile_count,
    type_funct=get_corporation_profile_type,
)
def insert_update_corporation_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    corporation_uuid = kwargs.get("corporation_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "external_id": kwargs["external_id"],
            "corporation_type": kwargs["corporation_type"],
            "business_name": kwargs["business_name"],
            "address": kwargs["address"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        for key in ["categories"]:
            if key in kwargs:
                cols[key] = kwargs[key]
        CorporationProfileModel(
            endpoint_id,
            corporation_uuid,
            **cols,
        ).save()
        return

    corporation_profile = kwargs.get("entity")
    actions = [
        CorporationProfileModel.updated_by.set(kwargs["updated_by"]),
        CorporationProfileModel.updated_at.set(pendulum.now("UTC")),
    ]

    # Map of kwargs keys to CorporationProfileModel attributes
    field_map = {
        "external_id": CorporationProfileModel.external_id,
        "corporation_type": CorporationProfileModel.corporation_type,
        "business_name": CorporationProfileModel.business_name,
        "categories": CorporationProfileModel.categories,
        "address": CorporationProfileModel.address,
    }

    # Add actions dynamically based on the presence of keys in kwargs
    for key, field in field_map.items():
        if key in kwargs:  # Check if the key exists in kwargs
            actions.append(field.set(None if kwargs[key] == "null" else kwargs[key]))

    corporation_profile.update(actions=actions)

    data = _insert_update_attribute_values(
        info,
        "corporation",
        corporation_uuid,
        kwargs["updated_by"],
        kwargs.get("data", {}),
    )
    info.context["logger"].info(f"Corporation profile data: {data} has been updated.")

    return


@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "corporation_uuid",
    },
    model_funct=get_corporation_profile,
)
def delete_corporation_profile(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True
