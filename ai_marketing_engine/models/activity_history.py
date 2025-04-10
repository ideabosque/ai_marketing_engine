#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
import time
from datetime import datetime
from typing import Any, Dict

import pendulum
from graphene import ResolveInfo
from pynamodb.attributes import (
    MapAttribute,
    NumberAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from tenacity import retry, stop_after_attempt, wait_exponential

from silvaengine_dynamodb_base import (
    BaseModel,
    delete_decorator,
    monitor_decorator,
    resolve_list_decorator,
)
from silvaengine_utility import Utility

from ..types.activity_history import ActivityHistoryListType, ActivityHistoryType


class TypeIdIndex(GlobalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "type-id-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    type = UnicodeAttribute(hash_key=True)
    id = UnicodeAttribute(range_key=True)


class ActivityHistoryModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-activity_history"

    id = UnicodeAttribute(hash_key=True)
    timestamp = NumberAttribute(range_key=True)
    log = UnicodeAttribute()
    data_diff = MapAttribute(default={})
    type = UnicodeAttribute()
    updated_by = UnicodeAttribute(null=True)
    updated_at = UTCDateTimeAttribute()
    type_id_index = TypeIdIndex()


def create_activity_history_table(logger: logging.Logger) -> bool:
    """Create the ActivityHistory table if it doesn't exist."""
    if not ActivityHistoryModel.exists():
        # Create with on-demand billing (PAY_PER_REQUEST)
        ActivityHistoryModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        logger.info("The ActivityHistory table has been created.")
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_activity_history(id: str, timestamp: int) -> ActivityHistoryModel:
    return ActivityHistoryModel.get(id, timestamp)


def get_activity_history_type(
    info: ResolveInfo, activity_history: ActivityHistoryModel
) -> ActivityHistoryType:
    activity_history = activity_history.__dict__["attribute_values"]
    return ActivityHistoryType(
        **Utility.json_loads(Utility.json_dumps(activity_history))
    )


def resolve_activity_history(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ActivityHistoryType:
    return get_activity_history_type(
        info,
        get_activity_history(kwargs.get("id"), kwargs.get("timestamp")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["id", "timestamp"],
    list_type_class=ActivityHistoryListType,
    type_funct=get_activity_history_type,
)
def resolve_activity_history_list(info: ResolveInfo, **kwargs: Dict[str, Any]) -> Any:
    id = kwargs.get("id")
    activity_type = kwargs.get("activity_type")
    log = kwargs.get("log")
    activity_types = None

    if activity_type is None:
        activity_types = kwargs.get("activity_types")

    args = []
    inquiry_funct = ActivityHistoryModel.scan
    count_funct = ActivityHistoryModel.count
    if id:
        args = [id, None]
        inquiry_funct = ActivityHistoryModel.query
    if activity_type and not id:
        args = [activity_type, None]
        inquiry_funct = ActivityHistoryModel.type_id_index.query
        count_funct = ActivityHistoryModel.type_id_index.count

    the_filters = None  # We can add filters for the query.
    if log:
        the_filters &= ActivityHistoryModel.log.contains(log)
    if activity_types:
        the_filters &= ActivityHistoryModel.type.is_in(*activity_types)
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


def insert_activity_history(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ActivityHistoryType:
    id = kwargs.get("id")
    updated_at = pendulum.now("UTC")
    timestamp = int(datetime.timestamp(updated_at))
    ActivityHistoryModel(
        id,
        timestamp,
        **{
            "log": kwargs.get("log"),
            "data_diff": kwargs.get("data_diff", {}),
            "type": kwargs.get("type"),
            "updated_by": kwargs.get("updated_by"),
            "updated_at": updated_at,
        },
    ).save()
    info.context.get("logger").info(
        f"The activity history with the id/timestamp ({id}/{timestamp}) is inserted at {time.strftime('%X')}."
    )

    return ActivityHistoryType(
        **Utility.json_loads(
            Utility.json_dumps(
                get_activity_history(id, timestamp).__dict__["attribute_values"]
            )
        )
    )


@delete_decorator(
    keys={
        "hash_key": "id",
        "range_key": "timestamp",
    },
    model_funct=get_activity_history,
)
def delete_activity_history(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True
