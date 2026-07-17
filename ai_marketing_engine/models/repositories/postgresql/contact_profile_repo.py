# -*- coding: utf-8 -*-
"""PostgreSQL repository for ContactProfile (with dynamic attributes)."""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, Optional

import pendulum

from ...postgresql.contact_profile import ContactProfileModel
from ..base import EntityRepository
from ._base import (
    _apply_pagination,
    _context_value,
    _gen_range_key,
    _get_partition_key,
    _normalize,
)
from .attribute_value_repo import insert_update_attribute_values

_UPDATABLE = ("email", "place_uuid", "first_name", "last_name")


class ContactProfilePGRepository(EntityRepository):
    """PostgreSQL repository for ContactProfile."""

    @property
    def entity_type(self) -> str:
        return "contact_profile"

    def _session(self):
        from ....handlers.config import Config

        return Config.db_session

    def get(self, **keys: Any) -> Optional[Dict[str, Any]]:
        partition_key = keys.get("partition_key")
        contact_uuid = keys.get("contact_uuid")
        if not partition_key or not contact_uuid:
            return None
        session = self._session()
        try:
            row = (
                session.query(ContactProfileModel)
                .filter(
                    ContactProfileModel.partition_key == partition_key,
                    ContactProfileModel.contact_uuid == contact_uuid,
                )
                .first()
            )
            return _normalize(row)
        except Exception:
            session.rollback()
            raise

    def count(self, **keys: Any) -> int:
        partition_key = keys.get("partition_key")
        contact_uuid = keys.get("contact_uuid")
        if not partition_key or not contact_uuid:
            return 0
        session = self._session()
        try:
            return (
                session.query(ContactProfileModel)
                .filter(
                    ContactProfileModel.partition_key == partition_key,
                    ContactProfileModel.contact_uuid == contact_uuid,
                )
                .count()
            )
        except Exception:
            session.rollback()
            raise

    def list(self, info: Any, **filters: Any) -> Any:
        from ....types.contact_profile import (
            ContactProfileListType,
            ContactProfileType,
        )

        session = self._session()
        page_number = filters.get("page_number", 1)
        limit = filters.get("limit", 10)
        partition_key = _get_partition_key(info)

        try:
            query = session.query(ContactProfileModel)
            if partition_key:
                query = query.filter(
                    ContactProfileModel.partition_key == partition_key
                )
            if filters.get("place_uuid"):
                query = query.filter(
                    ContactProfileModel.place_uuid == filters["place_uuid"]
                )
            if filters.get("email"):
                query = query.filter(ContactProfileModel.email == filters["email"])
            if filters.get("first_name"):
                query = query.filter(
                    ContactProfileModel.first_name.ilike(f"%{filters['first_name']}%")
                )
            if filters.get("last_name"):
                query = query.filter(
                    ContactProfileModel.last_name.ilike(f"%{filters['last_name']}%")
                )

            total = query.count()
            query = query.order_by(ContactProfileModel.updated_at.desc())
            query, _o, _l = _apply_pagination(query, page_number, limit)
            rows = query.all()

            contact_profile_list = [
                ContactProfileType(**_normalize(row)) for row in rows
            ]
            return ContactProfileListType(
                contact_profile_list=contact_profile_list,
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
        contact_uuid = kwargs.get("contact_uuid")
        explicit = contact_uuid is not None
        if not contact_uuid:
            contact_uuid = _gen_range_key()

        try:
            row = (
                session.query(ContactProfileModel)
                .filter(
                    ContactProfileModel.partition_key == partition_key,
                    ContactProfileModel.contact_uuid == contact_uuid,
                )
                .first()
            )

            if row is None:
                if explicit:
                    raise ValueError(
                        f"Cannot find the contact_profile with "
                        f"{partition_key}/{contact_uuid}."
                    )
                email = kwargs["email"]
                existing = (
                    session.query(ContactProfileModel)
                    .filter(
                        ContactProfileModel.partition_key == partition_key,
                        ContactProfileModel.email == email,
                    )
                    .first()
                )
                if existing is not None:
                    raise ValueError(
                        f"Contact profile with email '{email}' already exists "
                        f"for contact_uuid: {existing.contact_uuid}"
                    )
                now = pendulum.now("UTC")
                cols: Dict[str, Any] = {
                    "partition_key": partition_key,
                    "contact_uuid": contact_uuid,
                    "email": email,
                    "place_uuid": kwargs.get("place_uuid"),
                    "endpoint_id": _context_value(info, "endpoint_id"),
                    "part_id": kwargs.get("part_id", _context_value(info, "part_id")),
                    "updated_by": kwargs["updated_by"],
                    "created_at": now,
                    "updated_at": now,
                }
                for key in ("first_name", "last_name"):
                    if key in kwargs:
                        cols[key] = kwargs[key]
                row = ContactProfileModel(**cols)
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
                "contact",
                contact_uuid,
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
        contact_uuid = kwargs.get("contact_uuid")
        try:
            row = (
                session.query(ContactProfileModel)
                .filter(
                    ContactProfileModel.partition_key == partition_key,
                    ContactProfileModel.contact_uuid == contact_uuid,
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
        session = self._session()
        partition_key = _get_partition_key(info)
        try:
            if kwargs.get("email"):
                row = (
                    session.query(ContactProfileModel)
                    .filter(
                        ContactProfileModel.partition_key == partition_key,
                        ContactProfileModel.email == kwargs["email"],
                    )
                    .first()
                )
                return self.get_type(info, row) if row else None
        except Exception:
            session.rollback()
            raise

        data = self.get(partition_key=partition_key, contact_uuid=kwargs.get("contact_uuid"))
        return self.get_type(info, data) if data else None

    def get_type(self, info: Any, instance: Any) -> Any:
        from ....types.contact_profile import ContactProfileType

        data = instance if isinstance(instance, dict) else _normalize(instance)
        if data is None:
            return None
        return ContactProfileType(**data)


__all__ = ["ContactProfilePGRepository"]
