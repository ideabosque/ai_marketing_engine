# -*- coding: utf-8 -*-
"""PostgreSQL SQLAlchemy model for ActivityHistory (table: activity_history).

Mirrors the DynamoDB ``ActivityHistoryModel``. This is a global audit log
keyed by (id, timestamp) with **no** ``partition_key`` column, so it is NOT
subject to Row-Level Security tenant isolation.
"""
from __future__ import print_function

__author__ = "bibow"

from sqlalchemy import BigInteger, Column, Index, String, Text, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declared_attr

from .base import Base, prefixed_index, prefixed_table


class ActivityHistoryModel(Base):
    """SQLAlchemy model for ActivityHistory (table: <prefix>activity_history)."""

    @declared_attr
    def __tablename__(cls) -> str:
        return prefixed_table("activity_history")

    # Primary key: composite (id, timestamp)
    id = Column(String, nullable=False, primary_key=True)
    timestamp = Column(BigInteger, nullable=False, primary_key=True)

    log = Column(Text, nullable=True)
    data_diff = Column(JSONB, nullable=True)
    type = Column(String, nullable=True)
    updated_by = Column(String(64), nullable=True)
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )

    @declared_attr
    def __table_args__(cls):
        return (
            # GSI equivalent: type-id-index
            Index(
                prefixed_index("idx_activity_history_type_id"),
                "type",
                "id",
            ),
        )


__all__ = ["ActivityHistoryModel"]
