# -*- coding: utf-8 -*-
"""PostgreSQL repository for AttributeValue.

Implements the EntityRepository contract using SQLAlchemy against
``AttributeValueModel``. Also exposes ``insert_update_attribute_values`` /
``get_attributes_data`` helpers that mirror the DynamoDB attribute-versioning
semantics, used by the contact/corporation repositories.
"""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, List, Optional

import pendulum

from ...postgresql.attribute_value import AttributeValueModel
from ..base import EntityRepository
from ._base import (
    _apply_pagination,
    _context_value,
    _gen_range_key,
    _get_partition_key,
    _normalize,
)


def _get_active_attribute_value(
    session: Any, data_type_attribute_name: str, data_identity: str
) -> Optional[AttributeValueModel]:
    return (
        session.query(AttributeValueModel)
        .filter(
            AttributeValueModel.data_type_attribute_name == data_type_attribute_name,
            AttributeValueModel.data_identity == data_identity,
            AttributeValueModel.status == "active",
        )
        .order_by(AttributeValueModel.updated_at.desc())
        .first()
    )


def _inactivate_attribute_values(
    session: Any, data_type_attribute_name: str, data_identity: str
) -> None:
    session.query(AttributeValueModel).filter(
        AttributeValueModel.data_type_attribute_name == data_type_attribute_name,
        AttributeValueModel.data_identity == data_identity,
        AttributeValueModel.status == "active",
    ).update({AttributeValueModel.status: "inactive"}, synchronize_session=False)


def insert_update_attribute_values(
    session: Any,
    info: Any,
    data_type: str,
    data_identity: str,
    updated_by: str,
    data: Optional[Dict[str, Any]] = None,
    partition_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Insert/version dynamic attributes; returns ``{attribute_name: value}``.

    Mirrors the DynamoDB ``insert_update_attribute_values`` behavior: only
    writes a new active version when the value actually changed, inactivating
    the prior active version.
    """
    data = data or {}
    partition_key = partition_key or _get_partition_key(info)
    result: Dict[str, Any] = {}

    for attribute_name, value in data.items():
        dtan = f"{data_type}-{attribute_name}"
        active = _get_active_attribute_value(session, dtan, data_identity)
        if active is not None and active.value == value:
            result[attribute_name] = active.value
            continue

        if active is not None:
            _inactivate_attribute_values(session, dtan, data_identity)

        now = pendulum.now("UTC")
        row = AttributeValueModel(
            data_type_attribute_name=dtan,
            value_version_uuid=_gen_range_key(),
            data_identity=data_identity,
            partition_key=partition_key,
            value=value,
            status="active",
            updated_by=updated_by,
            created_at=now,
            updated_at=now,
        )
        session.add(row)
        result[attribute_name] = value

    session.flush()
    return result


def get_attributes_data(
    session: Any, partition_key: str, data_identity: str, data_type: str
) -> Dict[str, Any]:
    rows = (
        session.query(AttributeValueModel)
        .filter(
            AttributeValueModel.partition_key == partition_key,
            AttributeValueModel.data_identity == data_identity,
            AttributeValueModel.data_type_attribute_name.like(f"{data_type}-%"),
            AttributeValueModel.status == "active",
        )
        .all()
    )
    return {row.data_type_attribute_name.split("-", 1)[1]: row.value for row in rows}


class AttributeValuePGRepository(EntityRepository):
    """PostgreSQL repository for AttributeValue."""

    @property
    def entity_type(self) -> str:
        return "attribute_value"

    def _session(self):
        from ....handlers.config import Config

        return Config.db_session

    def get(self, **keys: Any) -> Optional[Dict[str, Any]]:
        dtan = keys.get("data_type_attribute_name")
        value_version_uuid = keys.get("value_version_uuid")
        if not dtan or not value_version_uuid:
            return None
        session = self._session()
        try:
            row = (
                session.query(AttributeValueModel)
                .filter(
                    AttributeValueModel.data_type_attribute_name == dtan,
                    AttributeValueModel.value_version_uuid == value_version_uuid,
                )
                .first()
            )
            return _normalize(row)
        except Exception:
            session.rollback()
            raise

    def count(self, **keys: Any) -> int:
        dtan = keys.get("data_type_attribute_name")
        value_version_uuid = keys.get("value_version_uuid")
        if not dtan or not value_version_uuid:
            return 0
        session = self._session()
        try:
            return (
                session.query(AttributeValueModel)
                .filter(
                    AttributeValueModel.data_type_attribute_name == dtan,
                    AttributeValueModel.value_version_uuid == value_version_uuid,
                )
                .count()
            )
        except Exception:
            session.rollback()
            raise

    def list(self, info: Any, **filters: Any) -> Any:
        from ....types.attribute_value import AttributeValueListType, AttributeValueType

        session = self._session()
        page_number = filters.get("page_number", 1)
        limit = filters.get("limit", 10)
        dtan = filters.get("data_type_attribute_name")
        data_identity = filters.get("data_identity")
        value = filters.get("value")
        statuses = filters.get("statuses")
        partition_key = _get_partition_key(info) or _context_value(info, "endpoint_id")

        try:
            query = session.query(AttributeValueModel)
            if dtan:
                query = query.filter(
                    AttributeValueModel.data_type_attribute_name == dtan
                )
            if data_identity:
                query = query.filter(
                    AttributeValueModel.data_identity == data_identity
                )
            if partition_key:
                query = query.filter(
                    AttributeValueModel.partition_key == partition_key
                )
            if value:
                query = query.filter(AttributeValueModel.value == value)
            if statuses:
                query = query.filter(AttributeValueModel.status.in_(statuses))

            total = query.count()
            query = query.order_by(AttributeValueModel.updated_at.desc())
            query, _o, _l = _apply_pagination(query, page_number, limit)
            rows = query.all()

            attribute_value_list = [
                AttributeValueType(**_normalize(row)) for row in rows
            ]
            return AttributeValueListType(
                attribute_value_list=attribute_value_list,
                total=total,
                page_size=limit,
                page_number=page_number,
            )
        except Exception:
            session.rollback()
            raise

    def insert_update(self, info: Any, **kwargs: Any) -> Any:
        session = self._session()
        dtan = kwargs.get("data_type_attribute_name")
        value_version_uuid = kwargs.get("value_version_uuid")
        explicit_version = value_version_uuid is not None
        if not value_version_uuid:
            value_version_uuid = _gen_range_key()

        partition_key = (
            kwargs.get("partition_key")
            or _get_partition_key(info)
            or _context_value(info, "endpoint_id")
        )
        try:
            row = (
                session.query(AttributeValueModel)
                .filter(
                    AttributeValueModel.data_type_attribute_name == dtan,
                    AttributeValueModel.value_version_uuid == value_version_uuid,
                )
                .first()
            )

            if row is None:
                if explicit_version:
                    raise ValueError(
                        f"Cannot find the attribute_value with "
                        f"{dtan}/{value_version_uuid}."
                    )
                data_identity = kwargs["data_identity"]
                cols: Dict[str, Any] = {}
                active = _get_active_attribute_value(session, dtan, data_identity)
                if active is not None:
                    excluded = {
                        "data_type_attribute_name",
                        "value_version_uuid",
                        "data_identity",
                        "partition_key",
                        "status",
                        "updated_by",
                        "created_at",
                        "updated_at",
                        "value",
                    }
                    for col in AttributeValueModel.__table__.columns:
                        if col.name not in excluded:
                            cols[col.name] = getattr(active, col.name, None)
                    _inactivate_attribute_values(session, dtan, data_identity)

                now = pendulum.now("UTC")
                row = AttributeValueModel(
                    data_type_attribute_name=dtan,
                    value_version_uuid=value_version_uuid,
                    data_identity=data_identity,
                    partition_key=partition_key,
                    value=kwargs.get("value"),
                    status="active",
                    updated_by=kwargs["updated_by"],
                    created_at=now,
                    updated_at=now,
                    **cols,
                )
                session.add(row)
            else:
                if (
                    kwargs.get("status") == "active"
                    and row.status == "inactive"
                ):
                    _inactivate_attribute_values(
                        session, dtan, row.data_identity
                    )
                for field in ("value", "status"):
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
        dtan = kwargs.get("data_type_attribute_name")
        value_version_uuid = kwargs.get("value_version_uuid")
        try:
            row = (
                session.query(AttributeValueModel)
                .filter(
                    AttributeValueModel.data_type_attribute_name == dtan,
                    AttributeValueModel.value_version_uuid == value_version_uuid,
                )
                .first()
            )
            if row is None:
                return True

            # If deleting the active version, promote the most recent inactive
            # one back to active (mirrors DynamoDB delete behavior).
            if row.status == "active":
                candidate = (
                    session.query(AttributeValueModel)
                    .filter(
                        AttributeValueModel.data_type_attribute_name == dtan,
                        AttributeValueModel.data_identity == row.data_identity,
                        AttributeValueModel.status == "inactive",
                    )
                    .order_by(AttributeValueModel.updated_at.desc())
                    .first()
                )
                if candidate is not None:
                    candidate.status = "active"

            session.delete(row)
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise

    def resolve_single(self, info: Any, **kwargs: Any) -> Any:
        session = self._session()
        if "data_identity" in kwargs:
            row = _get_active_attribute_value(
                session, kwargs["data_type_attribute_name"], kwargs["data_identity"]
            )
            return self.get_type(info, row) if row else None
        data = self.get(**kwargs)
        return self.get_type(info, data) if data else None

    def get_type(self, info: Any, instance: Any) -> Any:
        from ....types.attribute_value import AttributeValueType

        data = instance if isinstance(instance, dict) else _normalize(instance)
        if data is None:
            return None
        return AttributeValueType(**data)


__all__ = [
    "AttributeValuePGRepository",
    "insert_update_attribute_values",
    "get_attributes_data",
    "_get_active_attribute_value",
]
