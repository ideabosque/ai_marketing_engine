# -*- coding: utf-8 -*-
"""PostgreSQL SQLAlchemy model for ContactRequest (table: contact_requests).

Mirrors the DynamoDB ``ContactRequestModel``. Partition-keyed (RLS).
"""
from __future__ import print_function

__author__ = "bibow"

from sqlalchemy import Column, Index, String, Text, TIMESTAMP, text
from sqlalchemy.orm import declared_attr

from .base import Base, prefixed_index, prefixed_table


class ContactRequestModel(Base):
    """SQLAlchemy model for ContactRequest (table: <prefix>contact_requests)."""

    @declared_attr
    def __tablename__(cls) -> str:
        return prefixed_table("contact_requests")

    # Primary key: composite (partition_key, request_uuid)
    partition_key = Column(String(128), nullable=False, primary_key=True)
    request_uuid = Column(String, nullable=False, primary_key=True)

    contact_uuid = Column(String, nullable=False)
    place_uuid = Column(String, nullable=True)
    endpoint_id = Column(String(64), nullable=True)
    part_id = Column(String(64), nullable=True)
    request_title = Column(Text, nullable=True)
    request_detail = Column(Text, nullable=True)

    updated_by = Column(String(64), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )

    @declared_attr
    def __table_args__(cls):
        return (
            Index(
                prefixed_index("idx_contact_requests_partition_place_uuid"),
                "partition_key",
                "place_uuid",
            ),
            Index(
                prefixed_index("idx_contact_requests_partition_contact_uuid"),
                "partition_key",
                "contact_uuid",
            ),
        )


__all__ = ["ContactRequestModel"]
