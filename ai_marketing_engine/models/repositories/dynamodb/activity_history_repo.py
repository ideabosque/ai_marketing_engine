# -*- coding: utf-8 -*-
"""DynamoDB repository for ActivityHistory (thin wrapper over model funcs).

ActivityHistory is insert-only (no update) and has no ``partition_key``.
"""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, Optional

from ...dynamodb.activity_history import (
    delete_activity_history,
    get_activity_history,
    get_activity_history_type,
    insert_activity_history,
    resolve_activity_history,
    resolve_activity_history_list,
)
from ..base import EntityRepository
from ._base import _normalize


class ActivityHistoryRepository(EntityRepository):
    """DynamoDB repository for ActivityHistory."""

    @property
    def entity_type(self) -> str:
        return "activity_history"

    def get(self, **keys: Any) -> Optional[Dict[str, Any]]:
        id_ = keys.get("id")
        timestamp = keys.get("timestamp")
        if id_ is None or timestamp is None:
            return None
        return _normalize(get_activity_history(id_, timestamp))

    def count(self, **keys: Any) -> int:
        return 1 if self.get(**keys) else 0

    def list(self, info: Any, **filters: Any) -> Any:
        return resolve_activity_history_list(info, **filters)

    def insert(self, info: Any, **kwargs: Any) -> Any:
        return insert_activity_history(info, **kwargs)

    def insert_update(self, info: Any, **kwargs: Any) -> Any:
        return insert_activity_history(info, **kwargs)

    def delete(self, info: Any, **kwargs: Any) -> bool:
        return delete_activity_history(info, **kwargs)

    def resolve_single(self, info: Any, **kwargs: Any) -> Any:
        return resolve_activity_history(info, **kwargs)

    def get_type(self, info: Any, instance: Any) -> Any:
        return get_activity_history_type(info, instance)


__all__ = ["ActivityHistoryRepository"]
