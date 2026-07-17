# -*- coding: utf-8 -*-
"""PostgreSQL repository for ActivityHistory (insert-only, no partition_key)."""
from __future__ import print_function

__author__ = "bibow"

from datetime import datetime
from typing import Any, Dict, Optional

import pendulum

from ...postgresql.activity_history import ActivityHistoryModel
from ..base import EntityRepository
from ._base import _apply_pagination, _normalize


class ActivityHistoryPGRepository(EntityRepository):
    """PostgreSQL repository for ActivityHistory."""

    @property
    def entity_type(self) -> str:
        return "activity_history"

    def _session(self):
        from ....handlers.config import Config

        return Config.db_session

    def get(self, **keys: Any) -> Optional[Dict[str, Any]]:
        id_ = keys.get("id")
        timestamp = keys.get("timestamp")
        if id_ is None or timestamp is None:
            return None
        session = self._session()
        try:
            row = (
                session.query(ActivityHistoryModel)
                .filter(
                    ActivityHistoryModel.id == id_,
                    ActivityHistoryModel.timestamp == timestamp,
                )
                .first()
            )
            return _normalize(row)
        except Exception:
            session.rollback()
            raise

    def count(self, **keys: Any) -> int:
        return 1 if self.get(**keys) else 0

    def list(self, info: Any, **filters: Any) -> Any:
        from ....types.activity_history import (
            ActivityHistoryListType,
            ActivityHistoryType,
        )

        session = self._session()
        page_number = filters.get("page_number", 1)
        limit = filters.get("limit", 10)
        id_ = filters.get("id")
        activity_type = filters.get("activity_type")
        log = filters.get("log")
        activity_types = (
            filters.get("activity_types") if activity_type is None else None
        )

        try:
            query = session.query(ActivityHistoryModel)
            if id_:
                query = query.filter(ActivityHistoryModel.id == id_)
            if activity_type:
                query = query.filter(ActivityHistoryModel.type == activity_type)
            if log:
                query = query.filter(ActivityHistoryModel.log.ilike(f"%{log}%"))
            if activity_types:
                query = query.filter(ActivityHistoryModel.type.in_(activity_types))

            total = query.count()
            query = query.order_by(ActivityHistoryModel.timestamp.desc())
            query, _o, _l = _apply_pagination(query, page_number, limit)
            rows = query.all()

            activity_history_list = [
                ActivityHistoryType(**_normalize(row)) for row in rows
            ]
            return ActivityHistoryListType(
                activity_history_list=activity_history_list,
                total=total,
                page_size=limit,
                page_number=page_number,
            )
        except Exception:
            session.rollback()
            raise

    def insert(self, info: Any, **kwargs: Any) -> Any:
        session = self._session()
        id_ = kwargs.get("id")
        updated_at = pendulum.now("UTC")
        timestamp = int(datetime.timestamp(updated_at))
        try:
            row = ActivityHistoryModel(
                id=id_,
                timestamp=timestamp,
                log=kwargs.get("log"),
                data_diff=kwargs.get("data_diff", {}),
                type=kwargs.get("type"),
                updated_by=kwargs.get("updated_by"),
                updated_at=updated_at,
            )
            session.add(row)
            session.commit()
            return self.get_type(info, row)
        except Exception:
            session.rollback()
            raise

    def insert_update(self, info: Any, **kwargs: Any) -> Any:
        return self.insert(info, **kwargs)

    def delete(self, info: Any, **kwargs: Any) -> bool:
        session = self._session()
        id_ = kwargs.get("id")
        timestamp = kwargs.get("timestamp")
        try:
            row = (
                session.query(ActivityHistoryModel)
                .filter(
                    ActivityHistoryModel.id == id_,
                    ActivityHistoryModel.timestamp == timestamp,
                )
                .first()
            )
            if row is None:
                return True
            session.delete(row)
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise

    def resolve_single(self, info: Any, **kwargs: Any) -> Any:
        data = self.get(id=kwargs.get("id"), timestamp=kwargs.get("timestamp"))
        return self.get_type(info, data) if data else None

    def get_type(self, info: Any, instance: Any) -> Any:
        from ....types.activity_history import ActivityHistoryType

        data = instance if isinstance(instance, dict) else _normalize(instance)
        if data is None:
            return None
        return ActivityHistoryType(**data)


__all__ = ["ActivityHistoryPGRepository"]
