# -*- coding: utf-8 -*-
"""DynamoDB repository for AttributeValue (thin wrapper over model funcs)."""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, Optional

from ...dynamodb.attribute_value import (
    delete_attribute_value,
    get_attribute_value,
    get_attribute_value_count,
    get_attribute_value_type,
    insert_update_attribute_value,
    resolve_attribute_value,
    resolve_attribute_value_list,
)
from ..base import EntityRepository
from ._base import _normalize


class AttributeValueRepository(EntityRepository):
    """DynamoDB repository for AttributeValue."""

    @property
    def entity_type(self) -> str:
        return "attribute_value"

    def get(self, **keys: Any) -> Optional[Dict[str, Any]]:
        data_type_attribute_name = keys.get("data_type_attribute_name")
        value_version_uuid = keys.get("value_version_uuid")
        if not data_type_attribute_name or not value_version_uuid:
            return None
        if get_attribute_value_count(data_type_attribute_name, value_version_uuid) == 0:
            return None
        return _normalize(
            get_attribute_value(data_type_attribute_name, value_version_uuid)
        )

    def count(self, **keys: Any) -> int:
        data_type_attribute_name = keys.get("data_type_attribute_name")
        value_version_uuid = keys.get("value_version_uuid")
        if not data_type_attribute_name or not value_version_uuid:
            return 0
        return get_attribute_value_count(data_type_attribute_name, value_version_uuid)

    def list(self, info: Any, **filters: Any) -> Any:
        return resolve_attribute_value_list(info, **filters)

    def insert_update(self, info: Any, **kwargs: Any) -> Any:
        return insert_update_attribute_value(info, **kwargs)

    def delete(self, info: Any, **kwargs: Any) -> bool:
        return delete_attribute_value(info, **kwargs)

    def resolve_single(self, info: Any, **kwargs: Any) -> Any:
        return resolve_attribute_value(info, **kwargs)

    def get_type(self, info: Any, instance: Any) -> Any:
        return get_attribute_value_type(info, instance)


__all__ = ["AttributeValueRepository"]
