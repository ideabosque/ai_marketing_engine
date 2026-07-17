# -*- coding: utf-8 -*-
"""DynamoDB repository for the Place entity (thin wrapper over model funcs)."""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, Optional

from ...dynamodb.place import (
    delete_place,
    get_place,
    get_place_count,
    get_place_type,
    insert_update_place,
    resolve_place,
    resolve_place_list,
)
from ..base import EntityRepository
from ._base import _normalize


class PlaceRepository(EntityRepository):
    """DynamoDB repository for Place."""

    @property
    def entity_type(self) -> str:
        return "place"

    def get(self, **keys: Any) -> Optional[Dict[str, Any]]:
        partition_key = keys.get("partition_key")
        place_uuid = keys.get("place_uuid")
        if not partition_key or not place_uuid:
            return None
        if get_place_count(partition_key, place_uuid) == 0:
            return None
        return _normalize(get_place(partition_key, place_uuid))

    def count(self, **keys: Any) -> int:
        partition_key = keys.get("partition_key")
        place_uuid = keys.get("place_uuid")
        if not partition_key or not place_uuid:
            return 0
        return get_place_count(partition_key, place_uuid)

    def list(self, info: Any, **filters: Any) -> Any:
        return resolve_place_list(info, **filters)

    def insert_update(self, info: Any, **kwargs: Any) -> Any:
        return insert_update_place(info, **kwargs)

    def delete(self, info: Any, **kwargs: Any) -> bool:
        return delete_place(info, **kwargs)

    def resolve_single(self, info: Any, **kwargs: Any) -> Any:
        return resolve_place(info, **kwargs)

    def get_type(self, info: Any, instance: Any) -> Any:
        return get_place_type(info, instance)


__all__ = ["PlaceRepository"]
