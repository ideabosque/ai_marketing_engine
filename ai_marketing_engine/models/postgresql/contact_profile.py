# -*- coding: utf-8 -*-
"""PostgreSQL SQLAlchemy model for ContactProfile (table: contact_profiles).

Mirrors the DynamoDB ``ContactProfileModel``. Partition-keyed (RLS).
"""
from __future__ import print_function

__author__ = "bibow"

from sqlalchemy import Column, Index, String, TIMESTAMP, text
from sqlalchemy.orm import declared_attr

from .base import Base, prefixed_index, prefixed_table


class ContactProfileModel(Base):
    """SQLAlchemy model for ContactProfile (table: <prefix>contact_profiles)."""

    @declared_attr
    def __tablename__(cls) -> str:
        return prefixed_table("contact_profiles")

    # Primary key: composite (partition_key, contact_uuid)
    partition_key = Column(String(128), nullable=False, primary_key=True)
    contact_uuid = Column(String, nullable=False, primary_key=True)

    email = Column(String, nullable=False)
    place_uuid = Column(String, nullable=True)
    endpoint_id = Column(String(64), nullable=True)
    part_id = Column(String(64), nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

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
                prefixed_index("idx_contact_profiles_partition_email"),
                "partition_key",
                "email",
            ),
            Index(
                prefixed_index("idx_contact_profiles_partition_place_uuid"),
                "partition_key",
                "place_uuid",
            ),
        )


__all__ = ["ContactProfileModel"]
