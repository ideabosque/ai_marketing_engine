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
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex, LocalSecondaryIndex
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
from ..types.attribute_value import AttributeValueListType, AttributeValueType


class DataIdentityDataTypeAttributeNameIndex(GlobalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "data_identity-data_type_attribute_name-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    data_identity = UnicodeAttribute(hash_key=True)
    data_type_attribute_name = UnicodeAttribute(range_key=True)


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
    partition_key = UnicodeAttribute()
    value = UnicodeAttribute()
    status = UnicodeAttribute(default="active")
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    data_identity_index = DataIdentityIndex()
    data_identity_data_type_attribute_name_index = (
        DataIdentityDataTypeAttributeNameIndex()
    )


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
                    entity_keys["data_type_attribute_name"] = getattr(
                        entity, "data_type_attribute_name", None
                    )
                    entity_keys["value_version_uuid"] = getattr(
                        entity, "value_version_uuid", None
                    )

                # Fallback to kwargs (for creates/deletes)
                if not entity_keys.get("data_type_attribute_name"):
                    entity_keys["data_type_attribute_name"] = kwargs.get(
                        "data_type_attribute_name"
                    )
                if not entity_keys.get("value_version_uuid"):
                    entity_keys["value_version_uuid"] = kwargs.get("value_version_uuid")

                partition_key = args[0].context.get("endpoint_id") or kwargs.get(
                    "partition_key"
                )

                purge_entity_cascading_cache(
                    args[0].context.get("logger"),
                    entity_type="attribute_value",
                    context_keys=(
                        {"endpoint_id": partition_key} if partition_key else None
                    ),
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
    cache_name=Config.get_cache_name("models", "attribute_value"),
    cache_enabled=Config.is_cache_enabled,
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
def _get_attribute_value(
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
) -> AttributeValueModel | None:
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
    _ = info  # Keep for signature compatibility with decorators
    attribute_value_dict = attribute_value.__dict__["attribute_values"].copy()
    # Keep all fields including FKs - nested resolvers will handle lazy loading
    return AttributeValueType(**Serializer.json_normalize(attribute_value_dict))


def resolve_attribute_value(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> AttributeValueType | None:
    if "data_identity" in kwargs:
        return get_attribute_value_type(
            info,
            _get_active_attribute_value(
                kwargs["data_type_attribute_name"], kwargs["data_identity"]
            ),
        )

    count = get_attribute_value_count(
        kwargs["data_type_attribute_name"], kwargs["value_version_uuid"]
    )
    if count == 0:
        return None

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
    partition_key = info.context.get("partition_key") or info.context.get("endpoint_id")
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
    if partition_key:
        the_filters = AttributeValueModel.partition_key == partition_key
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
    model_funct=_get_attribute_value,
    count_funct=get_attribute_value_count,
    type_funct=get_attribute_value_type,
)
@purge_cache()
def insert_update_attribute_value(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    data_type_attribute_name = kwargs.get("data_type_attribute_name")
    value_version_uuid = kwargs.get("value_version_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "data_identity": kwargs["data_identity"],
            "partition_key": kwargs.get("partition_key")
            or info.context.get("partition_key")
            or info.context.get("endpoint_id"),
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
                "partition_key",
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
@purge_cache()
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


def purge_attributes_data_cache():
    def actual_decorator(original_function):
        @functools.wraps(original_function)
        def wrapper_function(*args, **kwargs):
            try:
                from ..models.cache import purge_entity_cascading_cache

                partition_key = args[0].context.get("partition_key") or args[
                    0
                ].context.get("endpoint_id")
                entity_keys = {}
                if kwargs.get("data_identity"):
                    entity_keys["data_identity"] = kwargs.get("data_identity")
                if kwargs.get("data_type"):
                    entity_keys["data_type"] = kwargs.get("data_type")

                result = purge_entity_cascading_cache(
                    args[0].context.get("logger"),
                    entity_type="attributes_data",
                    context_keys=(
                        {"endpoint_id": partition_key} if partition_key else None
                    ),
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


@purge_attributes_data_cache()
def insert_update_attribute_values(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    # Insert/update attribute values
    data_type = kwargs.get("data_type")
    data_identity = kwargs.get("data_identity")
    data = kwargs.get("data")
    updated_by = kwargs.get("updated_by")
    partition_key = kwargs.get("partition_key")
    attribute_values = []
    for attribute_name, value in data.items():
        active_attribute_value = _get_active_attribute_value(
            f"{data_type}-{attribute_name}", data_identity
        )
        if active_attribute_value and active_attribute_value.value == value:
            attribute_values.append(active_attribute_value)
            continue

        insert_params = {
            "data_type_attribute_name": f"{data_type}-{attribute_name}",
            "data_identity": data_identity,
            "value": value,
            "updated_by": updated_by,
        }
        if partition_key:
            insert_params["partition_key"] = partition_key

        attribute_value = insert_update_attribute_value(
            info,
            **insert_params,
        )
        attribute_values.append(attribute_value)

    return {
        attribute_value.data_type_attribute_name.split("-")[1]: attribute_value.value
        for attribute_value in attribute_values
    }


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
@method_cache(
    ttl=Config.get_cache_ttl(),
    cache_name=Config.get_cache_name("models", "attributes_data"),
    cache_enabled=Config.is_cache_enabled,
)
def get_attributes_data(
    partition_key: str,
    data_identity: str,
    data_type: str,
) -> Dict[str, Any]:
    results = AttributeValueModel.data_identity_data_type_attribute_name_index.query(
        hash_key=data_identity,
        range_key_condition=AttributeValueModel.data_type_attribute_name.startswith(
            data_type
        ),
        filter_condition=(
            (AttributeValueModel.status == "active")
            & (AttributeValueModel.partition_key == partition_key)
        ),
    )

    return {
        result.data_type_attribute_name.split("-")[1]: result.value
        for result in results
    }
