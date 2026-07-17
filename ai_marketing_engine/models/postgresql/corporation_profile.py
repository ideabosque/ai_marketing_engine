# -*- coding: utf-8 -*-
"""PostgreSQL SQLAlchemy model for CorporationProfile (table: corporation_profiles).

Mirrors the DynamoDB ``CorporationProfileModel``. Partition-keyed (RLS).
"""
from __future__ import print_function

__author__ = "bibow"

from sqlalchemy import Column, Index, String, Text, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declared_attr

from .base import Base, prefixed_index, prefixed_table


class CorporationProfileModel(Base):
    """SQLAlchemy model for CorporationProfile (table: <prefix>corporation_profiles)."""

    @declared_attr
    def __tablename__(cls) -> str:
        return prefixed_table("corporation_profiles")

    # Primary key: composite (partition_key, corporation_uuid)
    partition_key = Column(String(128), nullable=False, primary_key=True)
    corporation_uuid = Column(String, nullable=False, primary_key=True)

    external_id = Column(String, nullable=True)
    endpoint_id = Column(String(64), nullable=True)
    part_id = Column(String(64), nullable=True)
    corporation_type = Column(String, nullable=True)
    business_name = Column(Text, nullable=True)
    categories = Column(JSONB, nullable=True)
    address = Column(JSONB, nullable=True)

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
                prefixed_index("idx_corporation_profiles_partition_external_id"),
                "partition_key",
                "external_id",
            ),
            Index(
                prefixed_index("idx_corporation_profiles_partition_corporation_type"),
                "partition_key",
                "corporation_type",
            ),
        )


__all__ = ["CorporationProfileModel"]
