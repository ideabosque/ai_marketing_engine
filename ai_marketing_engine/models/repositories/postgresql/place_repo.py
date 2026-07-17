# -*- coding: utf-8 -*-
"""PostgreSQL repository for the Place entity."""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, Optional

import pendulum

from ...postgresql.place import PlaceModel
from ..base import EntityRepository
from ._base import (
    _apply_pagination,
    _context_value,
    _gen_range_key,
    _get_partition_key,
    _normalize,
)

_CREATE_OPTIONAL = ("phone_number", "types", "website", "corporation_uuid")
_UPDATABLE = (
    "region",
    "latitude",
    "longitude",
    "business_name",
    "address",
    "phone_number",
    "website",
    "types",
    "corporation_uuid",
)


class PlacePGRepository(EntityRepository):
    """PostgreSQL repository for Place."""

    @property
    def entity_type(self) -> str:
        return "place"

    def _session(self):
        from ....handlers.config import Config

        return Config.db_session

    def get(self, **keys: Any) -> Optional[Dict[str, Any]]:
        partition_key = keys.get("partition_key")
        place_uuid = keys.get("place_uuid")
        if not partition_key or not place_uuid:
            return None
        session = self._session()
        try:
            row = (
                session.query(PlaceModel)
                .filter(
                    PlaceModel.partition_key == partition_key,
                    PlaceModel.place_uuid == place_uuid,
                )
                .first()
            )
            return _normalize(row)
        except Exception:
            session.rollback()
            raise

    def count(self, **keys: Any) -> int:
        partition_key = keys.get("partition_key")
        place_uuid = keys.get("place_uuid")
        if not partition_key or not place_uuid:
            return 0
        session = self._session()
        try:
            return (
                session.query(PlaceModel)
                .filter(
                    PlaceModel.partition_key == partition_key,
                    PlaceModel.place_uuid == place_uuid,
                )
                .count()
            )
        except Exception:
            session.rollback()
            raise

    def list(self, info: Any, **filters: Any) -> Any:
        from ....types.place import PlaceListType, PlaceType

        session = self._session()
        page_number = filters.get("page_number", 1)
        limit = filters.get("limit", 10)
        partition_key = _get_partition_key(info)

        try:
            query = session.query(PlaceModel)
            if partition_key:
                query = query.filter(PlaceModel.partition_key == partition_key)
            if filters.get("region"):
                query = query.filter(PlaceModel.region == filters["region"])
            if filters.get("latitude"):
                query = query.filter(PlaceModel.latitude == filters["latitude"])
            if filters.get("longitude"):
                query = query.filter(PlaceModel.longitude == filters["longitude"])
            if filters.get("business_name"):
                query = query.filter(
                    PlaceModel.business_name.ilike(f"%{filters['business_name']}%")
                )
            if filters.get("address"):
                query = query.filter(
                    PlaceModel.address.ilike(f"%{filters['address']}%")
                )
            if filters.get("website"):
                query = query.filter(
                    PlaceModel.website.ilike(f"%{filters['website']}%")
                )
            if filters.get("corporation_uuid"):
                query = query.filter(
                    PlaceModel.corporation_uuid == filters["corporation_uuid"]
                )

            total = query.count()
            query = query.order_by(PlaceModel.updated_at.desc())
            query, _o, _l = _apply_pagination(query, page_number, limit)
            rows = query.all()

            place_list = [PlaceType(**_normalize(row)) for row in rows]
            return PlaceListType(
                place_list=place_list,
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
        place_uuid = kwargs.get("place_uuid")
        explicit = place_uuid is not None
        if not place_uuid:
            place_uuid = _gen_range_key()

        try:
            row = (
                session.query(PlaceModel)
                .filter(
                    PlaceModel.partition_key == partition_key,
                    PlaceModel.place_uuid == place_uuid,
                )
                .first()
            )

            if row is None:
                if explicit:
                    raise ValueError(
                        f"Cannot find the place with {partition_key}/{place_uuid}."
                    )
                now = pendulum.now("UTC")
                cols: Dict[str, Any] = {
                    "partition_key": partition_key,
                    "place_uuid": place_uuid,
                    "region": kwargs.get("region"),
                    "latitude": kwargs.get("latitude"),
                    "longitude": kwargs.get("longitude"),
                    "business_name": kwargs.get("business_name"),
                    "address": kwargs.get("address"),
                    "endpoint_id": _context_value(info, "endpoint_id"),
                    "part_id": _context_value(info, "part_id"),
                    "updated_by": kwargs["updated_by"],
                    "created_at": now,
                    "updated_at": now,
                }
                for key in _CREATE_OPTIONAL:
                    if key in kwargs:
                        cols[key] = kwargs[key]
                row = PlaceModel(**cols)
                session.add(row)
            else:
                for field in _UPDATABLE:
                    if field in kwargs:
                        val = kwargs[field]
                        setattr(row, field, None if val == "null" else val)
                row.updated_by = kwargs["updated_by"]
                row.updated_at = pendulum.now("UTC")

            session.commit()
            return self.get_type(info, row)
        except Exception:
            session.rollback()
            raise

    def delete(self, info: Any, **kwargs: Any) -> bool:
        session = self._session()
        partition_key = kwargs.get("partition_key") or _get_partition_key(info)
        place_uuid = kwargs.get("place_uuid")
        try:
            row = (
                session.query(PlaceModel)
                .filter(
                    PlaceModel.partition_key == partition_key,
                    PlaceModel.place_uuid == place_uuid,
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
        place_uuid = kwargs.get("place_uuid")
        data = self.get(partition_key=partition_key, place_uuid=place_uuid)
        return self.get_type(info, data) if data else None

    def get_type(self, info: Any, instance: Any) -> Any:
        from ....types.place import PlaceType

        data = instance if isinstance(instance, dict) else _normalize(instance)
        if data is None:
            return None
        return PlaceType(**data)


__all__ = ["PlacePGRepository"]
