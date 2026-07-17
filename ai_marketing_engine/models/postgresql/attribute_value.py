# -*- coding: utf-8 -*-
"""PostgreSQL SQLAlchemy model for AttributeValue (table: attribute_values).

Mirrors the DynamoDB ``AttributeValueModel``. The primary key is
(data_type_attribute_name, value_version_uuid); ``partition_key`` is a plain
column used for tenant isolation (RLS) and filtering.
"""
from __future__ import print_function

__author__ = "bibow"

from sqlalchemy import Column, Index, String, Text, TIMESTAMP, text
from sqlalchemy.orm import declared_attr

from .base import Base, prefixed_index, prefixed_table


class AttributeValueModel(Base):
    """SQLAlchemy model for AttributeValue (table: <prefix>attribute_values)."""

    @declared_attr
    def __tablename__(cls) -> str:
        return prefixed_table("attribute_values")

    # Primary key: composite (data_type_attribute_name, value_version_uuid)
    data_type_attribute_name = Column(String, nullable=False, primary_key=True)
    value_version_uuid = Column(String, nullable=False, primary_key=True)

    data_identity = Column(String, nullable=False)
    partition_key = Column(String(128), nullable=False)
    value = Column(Text, nullable=True)
    status = Column(String, nullable=False, server_default=text("'active'"))

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
            # LSI equivalent: data_identity-index (hash=data_type_attribute_name)
            Index(
                prefixed_index("idx_attribute_values_dtan_data_identity"),
                "data_type_attribute_name",
                "data_identity",
            ),
            # GSI equivalent: data_identity-data_type_attribute_name-index
            Index(
                prefixed_index("idx_attribute_values_data_identity_dtan"),
                "data_identity",
                "data_type_attribute_name",
            ),
            Index(
                prefixed_index("idx_attribute_values_partition_key"),
                "partition_key",
            ),
        )


__all__ = ["AttributeValueModel"]
