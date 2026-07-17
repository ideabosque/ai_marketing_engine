# -*- coding: utf-8 -*-
"""PostgreSQL repository for CorporationProfile (with dynamic attributes)."""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, Optional

import pendulum
from sqlalchemy import Text, cast

from ...postgresql.corporation_profile import CorporationProfileModel
from ..base import EntityRepository
from ._base import (
    _apply_pagination,
    _context_value,
    _gen_range_key,
    _get_partition_key,
    _normalize,
)
from .attribute_value_repo import insert_update_attribute_values

_UPDATABLE = (
    "external_id",
    "corporation_type",
    "business_name",
    "categories",
    "address",
)


class CorporationProfilePGRepository(EntityRepository):
    """PostgreSQL repository for CorporationProfile."""

    @property
    def entity_type(self) -> str:
        return "corporation_profile"

    def _session(self):
        from ....handlers.config import Config

        return Config.db_session

    def get(self, **keys: Any) -> Optional[Dict[str, Any]]:
        partition_key = keys.get("partition_key")
        corporation_uuid = keys.get("corporation_uuid")
        if not partition_key or not corporation_uuid:
            return None
        session = self._session()
        try:
            row = (
                session.query(CorporationProfileModel)
                .filter(
                    CorporationProfileModel.partition_key == partition_key,
                    CorporationProfileModel.corporation_uuid == corporation_uuid,
                )
                .first()
            )
            return _normalize(row)
        except Exception:
            session.rollback()
            raise

    def count(self, **keys: Any) -> int:
        partition_key = keys.get("partition_key")
        corporation_uuid = keys.get("corporation_uuid")
        if not partition_key or not corporation_uuid:
            return 0
        session = self._session()
        try:
            return (
                session.query(CorporationProfileModel)
                .filter(
                    CorporationProfileModel.partition_key == partition_key,
                    CorporationProfileModel.corporation_uuid == corporation_uuid,
                )
                .count()
            )
        except Exception:
            session.rollback()
            raise

    def list(self, info: Any, **filters: Any) -> Any:
        from ....types.corporation_profile import (
            CorporationProfileListType,
            CorporationProfileType,
        )

        session = self._session()
        page_number = filters.get("page_number", 1)
        limit = filters.get("limit", 10)
        partition_key = _get_partition_key(info)

        try:
            query = session.query(CorporationProfileModel)
            if partition_key:
                query = query.filter(
                    CorporationProfileModel.partition_key == partition_key
                )
            if filters.get("external_id"):
                query = query.filter(
                    CorporationProfileModel.external_id == filters["external_id"]
                )
            if filters.get("corporation_type"):
                query = query.filter(
                    CorporationProfileModel.corporation_type
                    == filters["corporation_type"]
                )
            if filters.get("business_name"):
                query = query.filter(
                    CorporationProfileModel.business_name == filters["business_name"]
                )
            if filters.get("category"):
                query = query.filter(
                    CorporationProfileModel.categories.contains([filters["category"]])
                )
            if filters.get("address"):
                query = query.filter(
                    cast(CorporationProfileModel.address, Text).ilike(
                        f"%{filters['address']}%"
                    )
                )

            total = query.count()
            query = query.order_by(CorporationProfileModel.updated_at.desc())
            query, _o, _l = _apply_pagination(query, page_number, limit)
            rows = query.all()

            corporation_profile_list = [
                CorporationProfileType(**_normalize(row)) for row in rows
            ]
            return CorporationProfileListType(
                corporation_profile_list=corporation_profile_list,
                total=total,
                page_size=limit,
                page_number=page_number,
            )
        except Exception:
            session.rollback()
            raise

    def insert_update(self, info: Any, **kwargs: Any) -> Any:
        session = self._session()
        partition_key = kwargs.get("partition_key") or _get_partition_key(info)
        corporation_uuid = kwargs.get("corporation_uuid")
        explicit = corporation_uuid is not None
        if not corporation_uuid:
            corporation_uuid = _gen_range_key()

        try:
            row = (
                session.query(CorporationProfileModel)
                .filter(
                    CorporationProfileModel.partition_key == partition_key,
                    CorporationProfileModel.corporation_uuid == corporation_uuid,
                )
                .first()
            )

            if row is None:
                if explicit:
                    raise ValueError(
                        f"Cannot find the corporation_profile with "
                        f"{partition_key}/{corporation_uuid}."
                    )
                now = pendulum.now("UTC")
                cols: Dict[str, Any] = {
                    "partition_key": partition_key,
                    "corporation_uuid": corporation_uuid,
                    "external_id": kwargs.get("external_id"),
                    "endpoint_id": _context_value(info, "endpoint_id"),
                    "part_id": kwargs.get("part_id", _context_value(info, "part_id")),
                    "corporation_type": kwargs.get("corporation_type"),
                    "business_name": kwargs.get("business_name"),
                    "address": kwargs.get("address"),
                    "updated_by": kwargs["updated_by"],
                    "created_at": now,
                    "updated_at": now,
                }
                if "categories" in kwargs:
                    cols["categories"] = kwargs["categories"]
                row = CorporationProfileModel(**cols)
                session.add(row)
            else:
                for field in _UPDATABLE:
                    if field in kwargs:
                        val = kwargs[field]
                        setattr(row, field, None if val == "null" else val)
                row.updated_by = kwargs["updated_by"]
                row.updated_at = pendulum.now("UTC")

            insert_update_attribute_values(
                session,
                info,
                "corporation",
                corporation_uuid,
                kwargs["updated_by"],
                kwargs.get("data", {}),
                partition_key,
            )

            session.commit()
            return self.get_type(info, row)
        except Exception:
            session.rollback()
            raise

    def delete(self, info: Any, **kwargs: Any) -> bool:
        session = self._session()
        partition_key = kwargs.get("partition_key") or _get_partition_key(info)
        corporation_uuid = kwargs.get("corporation_uuid")
        try:
            row = (
                session.query(CorporationProfileModel)
                .filter(
                    CorporationProfileModel.partition_key == partition_key,
                    CorporationProfileModel.corporation_uuid == corporation_uuid,
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
        partition_key = _get_partition_key(info)
        corporation_uuid = kwargs.get("corporation_uuid")
        data = self.get(partition_key=partition_key, corporation_uuid=corporation_uuid)
        return self.get_type(info, data) if data else None

    def get_type(self, info: Any, instance: Any) -> Any:
        from ....types.corporation_profile import CorporationProfileType

        data = instance if isinstance(instance, dict) else _normalize(instance)
        if data is None:
            return None
        return CorporationProfileType(**data)


__all__ = ["CorporationProfilePGRepository"]
