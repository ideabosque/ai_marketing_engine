# -*- coding: utf-8 -*-
"""PostgreSQL repository for ContactRequest."""
from __future__ import print_function

__author__ = "bibow"

import logging
from typing import Any, Dict, Optional

import pendulum

from ...postgresql.contact_profile import ContactProfileModel
from ...postgresql.contact_request import ContactRequestModel
from ...postgresql.place import PlaceModel
from ..base import EntityRepository
from ._base import (
    _apply_pagination,
    _context_value,
    _gen_range_key,
    _get_partition_key,
    _normalize,
)

_UPDATABLE = ("request_title", "request_detail", "place_uuid")


def _send_notification_emails(session: Any, info: Any, partition_key: str, **kwargs: Any) -> None:
    """Best-effort SES notification, mirroring the DynamoDB decorator."""
    if not (kwargs.get("notification_emails") and kwargs.get("source_email")):
        return
    try:
        from ....handlers.config import Config

        if not getattr(Config, "aws_ses", None):
            return

        contact = (
            session.query(ContactProfileModel)
            .filter(
                ContactProfileModel.partition_key == partition_key,
                ContactProfileModel.contact_uuid == kwargs["contact_uuid"],
            )
            .first()
        )
        contact_name = ""
        contact_email = "N/A"
        if contact is not None:
            contact_name = (
                f"{contact.first_name or ''} {contact.last_name or ''}".strip()
            )
            contact_email = contact.email or "N/A"

        place_info = "N/A"
        place_uuid = kwargs.get("place_uuid")
        if place_uuid:
            place = (
                session.query(PlaceModel)
                .filter(
                    PlaceModel.partition_key == partition_key,
                    PlaceModel.place_uuid == place_uuid,
                )
                .first()
            )
            if place is not None:
                place_info = f"{place.business_name or 'N/A'}, {place.address or 'N/A'}"
                if place.phone_number:
                    place_info += f", {place.phone_number}"
            else:
                place_info = place_uuid

        request_title = kwargs.get("request_title", "N/A")
        request_detail = kwargs.get("request_detail", "N/A")

        Config.aws_ses.send_email(
            Source=kwargs["source_email"],
            Destination={"ToAddresses": kwargs["notification_emails"]},
            Message={
                "Subject": {"Data": f"New Contact Request: {request_title}"},
                "Body": {
                    "Text": {
                        "Data": (
                            f"You have a new contact request:\n\n"
                            f"Title: {request_title}\n"
                            f"Detail: {request_detail}\n"
                            f"Place: {place_info}\n"
                            f"Contact: {contact_name} ({contact_email})"
                        )
                    }
                },
            },
        )
    except Exception as e:  # pragma: no cover - defensive
        logging.error(f"Failed to send notification email: {e}")


class ContactRequestPGRepository(EntityRepository):
    """PostgreSQL repository for ContactRequest."""

    @property
    def entity_type(self) -> str:
        return "contact_request"

    def _session(self):
        from ....handlers.config import Config

        return Config.db_session

    def get(self, **keys: Any) -> Optional[Dict[str, Any]]:
        partition_key = keys.get("partition_key")
        request_uuid = keys.get("request_uuid")
        if not partition_key or not request_uuid:
            return None
        session = self._session()
        try:
            row = (
                session.query(ContactRequestModel)
                .filter(
                    ContactRequestModel.partition_key == partition_key,
                    ContactRequestModel.request_uuid == request_uuid,
                )
                .first()
            )
            return _normalize(row)
        except Exception:
            session.rollback()
            raise

    def count(self, **keys: Any) -> int:
        partition_key = keys.get("partition_key")
        request_uuid = keys.get("request_uuid")
        if not partition_key or not request_uuid:
            return 0
        session = self._session()
        try:
            return (
                session.query(ContactRequestModel)
                .filter(
                    ContactRequestModel.partition_key == partition_key,
                    ContactRequestModel.request_uuid == request_uuid,
                )
                .count()
            )
        except Exception:
            session.rollback()
            raise

    def list(self, info: Any, **filters: Any) -> Any:
        from ....types.contact_request import (
            ContactRequestListType,
            ContactRequestType,
        )

        session = self._session()
        page_number = filters.get("page_number", 1)
        limit = filters.get("limit", 10)
        partition_key = _get_partition_key(info)

        try:
            query = session.query(ContactRequestModel)
            if partition_key:
                query = query.filter(
                    ContactRequestModel.partition_key == partition_key
                )
            if filters.get("contact_uuid"):
                query = query.filter(
                    ContactRequestModel.contact_uuid == filters["contact_uuid"]
                )
            if filters.get("place_uuid"):
                query = query.filter(
                    ContactRequestModel.place_uuid == filters["place_uuid"]
                )
            if filters.get("request_title"):
                query = query.filter(
                    ContactRequestModel.request_title.ilike(
                        f"%{filters['request_title']}%"
                    )
                )
            if filters.get("request_detail"):
                query = query.filter(
                    ContactRequestModel.request_detail.ilike(
                        f"%{filters['request_detail']}%"
                    )
                )

            total = query.count()
            query = query.order_by(ContactRequestModel.updated_at.desc())
            query, _o, _l = _apply_pagination(query, page_number, limit)
            rows = query.all()

            contact_request_list = [
                ContactRequestType(**_normalize(row)) for row in rows
            ]
            return ContactRequestListType(
                contact_request_list=contact_request_list,
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
        request_uuid = kwargs.get("request_uuid")
        explicit = request_uuid is not None
        if not request_uuid:
            request_uuid = _gen_range_key()

        try:
            contact_count = (
                session.query(ContactProfileModel)
                .filter(
                    ContactProfileModel.partition_key == partition_key,
                    ContactProfileModel.contact_uuid == kwargs["contact_uuid"],
                )
                .count()
            )
            assert contact_count == 1, "Contact profile not found."

            row = (
                session.query(ContactRequestModel)
                .filter(
                    ContactRequestModel.partition_key == partition_key,
                    ContactRequestModel.request_uuid == request_uuid,
                )
                .first()
            )

            if row is None:
                if explicit:
                    raise ValueError(
                        f"Cannot find the contact_request with "
                        f"{partition_key}/{request_uuid}."
                    )
                now = pendulum.now("UTC")
                row = ContactRequestModel(
                    partition_key=partition_key,
                    request_uuid=request_uuid,
                    contact_uuid=kwargs["contact_uuid"],
                    place_uuid=kwargs.get("place_uuid"),
                    endpoint_id=_context_value(info, "endpoint_id"),
                    part_id=_context_value(info, "part_id"),
                    request_title=kwargs["request_title"],
                    request_detail=kwargs["request_detail"],
                    updated_by=kwargs["updated_by"],
                    created_at=now,
                    updated_at=now,
                )
                session.add(row)
            else:
                for field in _UPDATABLE:
                    if kwargs.get(field) is not None:
                        setattr(row, field, kwargs[field])
                row.updated_by = kwargs["updated_by"]
                row.updated_at = pendulum.now("UTC")

            session.commit()
            _send_notification_emails(
                session, info, partition_key, **kwargs
            )
            return self.get_type(info, row)
        except Exception:
            session.rollback()
            raise

    def delete(self, info: Any, **kwargs: Any) -> bool:
        session = self._session()
        partition_key = kwargs.get("partition_key") or _get_partition_key(info)
        request_uuid = kwargs.get("request_uuid")
        try:
            row = (
                session.query(ContactRequestModel)
                .filter(
                    ContactRequestModel.partition_key == partition_key,
                    ContactRequestModel.request_uuid == request_uuid,
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
        data = self.get(partition_key=partition_key, request_uuid=kwargs.get("request_uuid"))
        return self.get_type(info, data) if data else None

    def get_type(self, info: Any, instance: Any) -> Any:
        from ....types.contact_request import ContactRequestType

        data = instance if isinstance(instance, dict) else _normalize(instance)
        if data is None:
            return None
        return ContactRequestType(**data)


__all__ = ["ContactRequestPGRepository"]
