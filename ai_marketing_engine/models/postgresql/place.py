# -*- coding: utf-8 -*-
"""PostgreSQL SQLAlchemy model for the Place entity (table: places).

Mirrors the DynamoDB ``PlaceModel`` schema. Partition-keyed (RLS-protected).
"""
from __future__ import print_function

__author__ = "bibow"

from sqlalchemy import Column, Index, String, Text, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declared_attr

from .base import Base, prefixed_index, prefixed_table


class PlaceModel(Base):
    """SQLAlchemy model for the Place entity (table: <prefix>places)."""

    @declared_attr
    def __tablename__(cls) -> str:
        return prefixed_table("places")

    # Primary key: composite (partition_key, place_uuid)
    partition_key = Column(String(128), nullable=False, primary_key=True)
    place_uuid = Column(String, nullable=False, primary_key=True)

    endpoint_id = Column(String(64), nullable=True)
    part_id = Column(String(64), nullable=True)
    region = Column(String, nullable=True)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    business_name = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    phone_number = Column(String, nullable=True)
    website = Column(String, nullable=True)
    types = Column(JSONB, nullable=True)
    corporation_uuid = Column(String, nullable=True)

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
            # LSI equivalent: region-index
            Index(
                prefixed_index("idx_places_partition_region"),
                "partition_key",
                "region",
            ),
            Index(
                prefixed_index("idx_places_partition_corporation_uuid"),
                "partition_key",
                "corporation_uuid",
            ),
        )


__all__ = ["PlaceModel"]
