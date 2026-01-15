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
from pynamodb.attributes import (
    ListAttribute,
    MapAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.indexes import AllProjection, LocalSecondaryIndex
from silvaengine_dynamodb_base import (
    BaseModel,
    delete_decorator,
    insert_update_decorator,
    monitor_decorator,
    resolve_list_decorator,
)
from silvaengine_utility import method_cache
from silvaengine_utility.serializer import Serializer
from tenacity import retry, stop_after_attempt, wait_exponential

from ..handlers.config import Config
from ..types.corporation_profile import (
    CorporationProfileListType,
    CorporationProfileType,
)
from .utils import insert_update_attribute_values


class CorporationTypeIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "corporation_type-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    partition_key = UnicodeAttribute(hash_key=True)
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
    partition_key = UnicodeAttribute(hash_key=True)
    external_id = UnicodeAttribute(range_key=True)


class CorporationProfileModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-corporation_profiles"

    partition_key = UnicodeAttribute(hash_key=True)
    corporation_uuid = UnicodeAttribute(range_key=True)
    external_id = UnicodeAttribute()
    endpoint_id = UnicodeAttribute()
    part_id = UnicodeAttribute()
    corporation_type = UnicodeAttribute()
    business_name = UnicodeAttribute()
    categories = ListAttribute(of=UnicodeAttribute, null=True)
    address = MapAttribute()
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    external_id_index = ExternalIdIndex()
    corporation_type_index = CorporationTypeIndex()


def purge_cache():
    def actual_decorator(original_function):
        @functools.wraps(original_function)
        def wrapper_function(*args, **kwargs):
            try:
                # Execute original function first
                result = original_function(*args, **kwargs)

                # Then purge cache after successful operation
                from ..models.cache import purge_entity_cascading_cache

                # Get entity keys from entity parameter (for updates)
                entity_keys = {}
                entity = kwargs.get("entity")
                if entity:
                    entity_keys["corporation_uuid"] = getattr(
                        entity, "corporation_uuid", None
                    )

                # Fallback to kwargs (for creates/deletes)
                if not entity_keys.get("corporation_uuid"):
                    entity_keys["corporation_uuid"] = kwargs.get("corporation_uuid")

                partition_key = args[0].context.get("partition_key")

                purge_entity_cascading_cache(
                    args[0].context.get("logger"),
                    entity_type="corporation_profile",
                    context_keys={"partition_key": partition_key},
                    entity_keys=entity_keys if entity_keys else None,
                    cascade_depth=3,
                )

                return result
            except Exception as e:
                log = traceback.format_exc()
                args[0].context.get("logger").error(log)
                raise e

        return wrapper_function

    return actual_decorator


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
@method_cache(
    ttl=Config.get_cache_ttl(),
    cache_name=Config.get_cache_name("models", "corporation_profile"),
    cache_enabled=Config.is_cache_enabled,
)
def get_corporation_profile(
    partition_key: str, corporation_uuid: str
) -> CorporationProfileModel:
    return CorporationProfileModel.get(partition_key, corporation_uuid)


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def _get_corporation_profile(
    partition_key: str, corporation_uuid: str
) -> CorporationProfileModel:
    return CorporationProfileModel.get(partition_key, corporation_uuid)


def get_corporation_profile_count(partition_key: str, corporation_uuid: str) -> int:
    return CorporationProfileModel.count(
        partition_key, CorporationProfileModel.corporation_uuid == corporation_uuid
    )


def get_corporation_profile_type(
    info: ResolveInfo, corporation_profile: CorporationProfileModel
) -> CorporationProfileType:
    """
    Nested resolver approach: return minimal corporation_profile data.
    - Do NOT embed 'data' here anymore.
    'data' is resolved lazily by CorporationProfileType.resolve_data.
    """
    try:
        corp_dict = corporation_profile.__dict__["attribute_values"]
    except Exception:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise

    return CorporationProfileType(**Serializer.json_normalize(corp_dict))


def resolve_corporation_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CorporationProfileType | None:
    partition_key = info.context["partition_key"]
    count = get_corporation_profile_count(partition_key, kwargs.get("corporation_uuid"))
    if count == 0:
        return None

    return get_corporation_profile_type(
        info,
        get_corporation_profile(partition_key, kwargs.get("corporation_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=[
        "partition_key",
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
    partition_key = info.context["partition_key"]
    external_id = kwargs.get("external_id")
    corporation_type = kwargs.get("corporation_type")
    business_name = kwargs.get("business_name")
    category = kwargs.get("category")
    address = kwargs.get("address")

    args = []
    inquiry_funct = CorporationProfileModel.scan
    count_funct = CorporationProfileModel.count
    if partition_key:
        args = [partition_key, None]
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
        "hash_key": "partition_key",
        "range_key": "corporation_uuid",
    },
    model_funct=_get_corporation_profile,
    count_funct=get_corporation_profile_count,
    type_funct=get_corporation_profile_type,
)
@purge_cache()
def insert_update_corporation_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    partition_key = kwargs.get("partition_key")
    corporation_uuid = kwargs.get("corporation_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "external_id": kwargs["external_id"],
            "endpoint_id": info.context.get("endpoint_id"),
            "part_id": kwargs.get("part_id", info.context.get("part_id")),
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
            partition_key,
            corporation_uuid,
            **cols,
        ).save()

        # Handle dynamic attributes (data field)
        data = insert_update_attribute_values(
            info,
            "corporation",
            corporation_uuid,
            kwargs["updated_by"],
            kwargs.get("data", {}),
            partition_key,
        )
        info.context["logger"].info(
            f"Corporation profile data: {data} has been updated."
        )

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

    data = insert_update_attribute_values(
        info,
        "corporation",
        corporation_uuid,
        kwargs["updated_by"],
        kwargs.get("data", {}),
        corporation_profile.partition_key,
    )
    info.context["logger"].info(f"Corporation profile data: {data} has been updated.")

    return


@delete_decorator(
    keys={
        "hash_key": "partition_key",
        "range_key": "corporation_uuid",
    },
    model_funct=get_corporation_profile,
)
@purge_cache()
def delete_corporation_profile(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True
