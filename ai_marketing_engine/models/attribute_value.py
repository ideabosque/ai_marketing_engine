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

from ..types.attribute_value import AttributeValueListType, AttributeValueType


class DataIdentityIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "data_identity-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    data_type_attribute_name = UnicodeAttribute(hash_key=True)
    data_identity = UnicodeAttribute(range_key=True)


class AttributeValueModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-attribute_values"

    data_type_attribute_name = UnicodeAttribute(hash_key=True)
    value_version_uuid = UnicodeAttribute(range_key=True)
    data_identity = UnicodeAttribute()
    endpoint_id = UnicodeAttribute()
    value = UnicodeAttribute()
    status = UnicodeAttribute(default="active")
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    data_identity_index = DataIdentityIndex()


def create_attribute_value_table(logger: logging.Logger) -> bool:
    """Create the AttributeValue table if it doesn't exist."""
    if not AttributeValueModel.exists():
        # Create with on-demand billing (PAY_PER_REQUEST)
        AttributeValueModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        logger.info("The AttributeValue table has been created.")
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_attribute_value(
    data_type_attribute_name: str, value_version_uuid: str
) -> AttributeValueModel:
    return AttributeValueModel.get(data_type_attribute_name, value_version_uuid)


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def _get_active_attribute_value(
    data_type_attribute_name: str, data_identity: str
) -> AttributeValueModel:
    try:
        results = AttributeValueModel.data_identity_index.query(
            data_type_attribute_name,
            AttributeValueModel.data_identity == data_identity,
            filter_condition=(AttributeValueModel.status == "active"),
            scan_index_forward=False,
            limit=1,
        )
        attribute_value = next(results)

        return attribute_value
    except StopIteration:
        return None


def get_attribute_value_count(
    data_type_attribute_name: str, value_version_uuid: str
) -> int:
    return AttributeValueModel.count(
        data_type_attribute_name,
        AttributeValueModel.value_version_uuid == value_version_uuid,
    )


def get_attribute_value_type(
    info: ResolveInfo, attribute_value: AttributeValueModel
) -> AttributeValueType:
    try:
        attribute_value = attribute_value.__dict__["attribute_values"]
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e

    return AttributeValueType(**Utility.json_loads(Utility.json_dumps(attribute_value)))


def resolve_attribute_value(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> AttributeValueType:
    if "data_identity" in kwargs:
        return get_attribute_value_type(
            info,
            _get_active_attribute_value(
                kwargs["data_type_attribute_name"], kwargs["data_identity"]
            ),
        )

    return get_attribute_value_type(
        info,
        get_attribute_value(
            kwargs["data_type_attribute_name"], kwargs["value_version_uuid"]
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=[
        "data_type_attribute_name",
        "value_version_uuid",
        "data_identity",
    ],
    list_type_class=AttributeValueListType,
    type_funct=get_attribute_value_type,
)
def resolve_attribute_value_list(info: ResolveInfo, **kwargs: Dict[str, Any]) -> Any:
    data_type_attribute_name = kwargs["data_type_attribute_name"]
    data_identity = kwargs.get("data_identity")
    endpoint_id = info.context["endpoint_id"]
    value = kwargs.get("value")
    statuses = kwargs.get("statuses")

    args = []
    inquiry_funct = AttributeValueModel.scan
    count_funct = AttributeValueModel.count
    if data_type_attribute_name:
        args = [data_type_attribute_name, None]
        inquiry_funct = AttributeValueModel.query
        if data_identity:
            inquiry_funct = AttributeValueModel.data_identity_index.query
            args[1] = AttributeValueModel.data_identity == data_identity
            count_funct = AttributeValueModel.data_identity_index.count

    the_filters = None
    if endpoint_id:
        the_filters = AttributeValueModel.endpoint_id == endpoint_id
    if value:
        value_filter = AttributeValueModel.value == value
        the_filters = (
            value_filter if the_filters is None else the_filters & value_filter
        )
    if statuses:
        status_filter = AttributeValueModel.status.is_in(*statuses)
        the_filters = (
            status_filter if the_filters is None else the_filters & status_filter
        )
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


def _inactivate_attribute_values(
    info: ResolveInfo, data_type_attribute_name: str, data_identity: str
) -> None:
    try:
        attribute_values = AttributeValueModel.data_identity_index.query(
            data_type_attribute_name,
            AttributeValueModel.data_identity == data_identity,
            filter_condition=AttributeValueModel.status == "active",
        )
        with AttributeValueModel.batch_write() as batch:
            for attribute_value in attribute_values:
                attribute_value.status = "inactive"
                batch.save(attribute_value)
        return
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").error(log)
        raise e


@insert_update_decorator(
    keys={
        "hash_key": "data_type_attribute_name",
        "range_key": "value_version_uuid",
    },
    model_funct=get_attribute_value,
    count_funct=get_attribute_value_count,
    type_funct=get_attribute_value_type,
)
def insert_update_attribute_value(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    data_type_attribute_name = kwargs.get("data_type_attribute_name")
    value_version_uuid = kwargs.get("value_version_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "data_identity": kwargs["data_identity"],
            "endpoint_id": info.context["endpoint_id"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
            "status": "active",
        }

        active_attribute_value = None
        if "data_identity" in kwargs:
            active_attribute_value = _get_active_attribute_value(
                data_type_attribute_name, kwargs["data_identity"]
            )
        if active_attribute_value:
            excluded_fields = {
                "data_type_attribute_name",
                "value_version_uuid",
                "data_identity",
                "endpoint_id",
                "status",
                "updated_by",
                "created_at",
                "updated_at",
            }

            cols.update(
                {
                    k: v
                    for k, v in active_attribute_value.__dict__[
                        "attribute_values"
                    ].items()
                    if k not in excluded_fields
                }
            )

            _inactivate_attribute_values(
                info, data_type_attribute_name, kwargs["data_identity"]
            )

        if "value" in kwargs:
            cols["value"] = kwargs["value"]

        attribute_value = AttributeValueModel(
            data_type_attribute_name,
            value_version_uuid,
            **cols,
        )
        attribute_value.save()
        return

    attribute_value = kwargs.get("entity")
    actions = [
        AttributeValueModel.updated_by.set(kwargs["updated_by"]),
        AttributeValueModel.updated_at.set(pendulum.now("UTC")),
    ]

    if "status" in kwargs and (
        kwargs["status"] == "active" and attribute_value.status == "inactive"
    ):
        _inactivate_attribute_values(
            info, data_type_attribute_name, attribute_value.data_identity
        )

    field_map = {
        "value": AttributeValueModel.value,
        "status": AttributeValueModel.status,
    }

    for key, field in field_map.items():
        if key in kwargs:
            actions.append(field.set(None if kwargs[key] == "null" else kwargs[key]))

    attribute_value.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "data_type_attribute_name",
        "range_key": "value_version_uuid",
    },
    model_funct=get_attribute_value,
)
def delete_attribute_value(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:

    if kwargs["entity"].status == "active":
        results = AttributeValueModel.data_identity_index.query(
            kwargs["entity"].data_type_attribute_name,
            AttributeValueModel.data_identity == kwargs["entity"].data_identity,
            filter_condition=(AttributeValueModel.status == "inactive"),
        )
        attribute_values = [result for result in results]
        if len(attribute_values) > 0:
            attribute_values = sorted(
                attribute_values, key=lambda x: x.updated_at, reverse=True
            )
            last_updated_record = attribute_values[0]
            last_updated_record.status = "active"
            last_updated_record.save()

    kwargs["entity"].delete()
    return True
