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

from ..types.utm_tag_data_collection import (
    UtmTagDataCollectionListType,
    UtmTagDataCollectionType,
)
from .utils import _get_contact_profile


class TageNameIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "tag_naame-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    endpoint_id = UnicodeAttribute(hash_key=True)
    tag_name = UnicodeAttribute(range_key=True)


class UtmTagDataCollectionModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-utm_tag_data_collection"

    endpoint_id = UnicodeAttribute(hash_key=True)
    collection_uuid = UnicodeAttribute(range_key=True)
    tag_name = UnicodeAttribute()
    place_uuid = UnicodeAttribute()
    contact_uuid = UnicodeAttribute()
    keyword = UnicodeAttribute()
    utm_campaign = UnicodeAttribute()
    utm_content = UnicodeAttribute()
    utm_medium = UnicodeAttribute()
    utm_source = UnicodeAttribute()
    utm_term = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    tag_name_index = TageNameIndex()


def create_utm_tag_data_collection_table(logger: logging.Logger) -> bool:
    """Create the UtmTagDataCollection table if it doesn't exist."""
    if not UtmTagDataCollectionModel.exists():
        # Create with on-demand billing (PAY_PER_REQUEST)
        UtmTagDataCollectionModel.create_table(
            billing_mode="PAY_PER_REQUEST", wait=True
        )
        logger.info("The UtmTagDataCollection table has been created.")
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_utm_tag_data_collection(
    endpoint_id: str, collection_uuid: str
) -> UtmTagDataCollectionModel:
    return UtmTagDataCollectionModel.get(endpoint_id, collection_uuid)


def get_utm_tag_data_collection_count(endpoint_id: str, collection_uuid: str) -> int:
    return UtmTagDataCollectionModel.count(
        endpoint_id,
        UtmTagDataCollectionModel.collection_uuid == collection_uuid,
    )


def get_utm_tag_data_collection_type(
    info: ResolveInfo, utm_tag_data_collection: UtmTagDataCollectionModel
) -> UtmTagDataCollectionType:
    try:
        contact_profile = _get_contact_profile(
            utm_tag_data_collection.endpoint_id, utm_tag_data_collection.contact_uuid
        )
        utm_tag_data_collection = utm_tag_data_collection.__dict__["attribute_values"]
        utm_tag_data_collection["contact_profile"] = contact_profile
        utm_tag_data_collection.pop("place_uuid")
        utm_tag_data_collection.pop("contact_uuid")
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e

    return UtmTagDataCollectionType(
        **Utility.json_normalize(utm_tag_data_collection)
    )


def resolve_utm_tag_data_collection(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> UtmTagDataCollectionType:
    count = get_utm_tag_data_collection_count(
        info.context["endpoint_id"], kwargs.get("collection_uuid")
    )
    if count == 0:
        return None

    return get_utm_tag_data_collection_type(
        info,
        get_utm_tag_data_collection(
            info.context["endpoint_id"], kwargs.get("collection_uuid")
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "collection_uuid", "tag_name"],
    list_type_class=UtmTagDataCollectionListType,
    type_funct=get_utm_tag_data_collection_type,
)
def resolve_utm_tag_data_collection_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    endpoint_id = info.context["endpoint_id"]
    tag_name = kwargs.get("tag_name")
    place_uuids = kwargs.get("place_uuids")
    contact_uuids = kwargs.get("contact_uuids")
    keyword = kwargs.get("keyword")

    args = []
    inquiry_funct = UtmTagDataCollectionModel.scan
    count_funct = UtmTagDataCollectionModel.count
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = UtmTagDataCollectionModel.query
        if tag_name:
            inquiry_funct = UtmTagDataCollectionModel.tag_name_index.query
            args[1] = UtmTagDataCollectionModel.tag_name == tag_name
            count_funct = UtmTagDataCollectionModel.tag_name_index.count

    the_filters = None  # We can add filters for the query.
    if place_uuids:
        the_filters &= UtmTagDataCollectionModel.place_uuid.is_in(*place_uuids)
    if contact_uuids:
        the_filters &= UtmTagDataCollectionModel.contact_uuid.is_in(*contact_uuids)
    if keyword:
        the_filters &= UtmTagDataCollectionModel.keyword.contains(keyword)
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "collection_uuid",
    },
    model_funct=get_utm_tag_data_collection,
    count_funct=get_utm_tag_data_collection_count,
    type_funct=get_utm_tag_data_collection_type,
)
def insert_utm_tag_data_collection(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    collection_uuid = kwargs.get("collection_uuid")
    if kwargs.get("entity") is None:
        UtmTagDataCollectionModel(
            endpoint_id,
            collection_uuid,
            **{
                "tag_name": kwargs["tag_name"],
                "place_uuid": kwargs["place_uuid"],
                "contact_uuid": kwargs["contact_uuid"],
                "keyword": kwargs["keyword"],
                "utm_campaign": kwargs["utm_campaign"],
                "utm_content": kwargs["utm_content"],
                "utm_medium": kwargs["utm_medium"],
                "utm_source": kwargs["utm_source"],
                "utm_term": kwargs["utm_term"],
                "created_at": pendulum.now("UTC"),
            },
        ).save()
        return

    return


@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "collection_uuid",
    },
    model_funct=get_utm_tag_data_collection,
)
def delete_utm_tag_data_collection(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True
