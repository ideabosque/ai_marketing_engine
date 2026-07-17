# -*- coding: utf-8 -*-
"""Create attribute_values table (partition_key column, RLS-protected)

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-16 00:05:00.000000
"""
from __future__ import print_function

__author__ = "bibow"

import os

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

_PREFIX = os.environ.get("PG_TABLE_PREFIX", "ame_")
_T = f"{_PREFIX}attribute_values"


def upgrade() -> None:
    op.create_table(
        _T,
        sa.Column("data_type_attribute_name", sa.String(), primary_key=True),
        sa.Column("value_version_uuid", sa.String(), primary_key=True),
        sa.Column("data_identity", sa.String(), nullable=False),
        sa.Column("partition_key", sa.String(128), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'active'")),
        sa.Column("updated_by", sa.String(64), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index(f"{_PREFIX}idx_attribute_values_dtan_data_identity", _T, ["data_type_attribute_name", "data_identity"])
    op.create_index(f"{_PREFIX}idx_attribute_values_data_identity_dtan", _T, ["data_identity", "data_type_attribute_name"])
    op.create_index(f"{_PREFIX}idx_attribute_values_partition_key", _T, ["partition_key"])


def downgrade() -> None:
    op.drop_index(f"{_PREFIX}idx_attribute_values_partition_key", table_name=_T)
    op.drop_index(f"{_PREFIX}idx_attribute_values_data_identity_dtan", table_name=_T)
    op.drop_index(f"{_PREFIX}idx_attribute_values_dtan_data_identity", table_name=_T)
    op.drop_table(_T)
