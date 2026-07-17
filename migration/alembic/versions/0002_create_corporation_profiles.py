# -*- coding: utf-8 -*-
"""Create corporation_profiles table (partition-keyed)

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-16 00:02:00.000000
"""
from __future__ import print_function

__author__ = "bibow"

import os

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

_PREFIX = os.environ.get("PG_TABLE_PREFIX", "ame_")
_T = f"{_PREFIX}corporation_profiles"


def upgrade() -> None:
    op.create_table(
        _T,
        sa.Column("partition_key", sa.String(128), primary_key=True),
        sa.Column("corporation_uuid", sa.String(), primary_key=True),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("endpoint_id", sa.String(64), nullable=True),
        sa.Column("part_id", sa.String(64), nullable=True),
        sa.Column("corporation_type", sa.String(), nullable=True),
        sa.Column("business_name", sa.Text(), nullable=True),
        sa.Column("categories", postgresql.JSONB, nullable=True),
        sa.Column("address", postgresql.JSONB, nullable=True),
        sa.Column("updated_by", sa.String(64), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index(f"{_PREFIX}idx_corporation_profiles_partition_external_id", _T, ["partition_key", "external_id"])
    op.create_index(f"{_PREFIX}idx_corporation_profiles_partition_corporation_type", _T, ["partition_key", "corporation_type"])


def downgrade() -> None:
    op.drop_index(f"{_PREFIX}idx_corporation_profiles_partition_corporation_type", table_name=_T)
    op.drop_index(f"{_PREFIX}idx_corporation_profiles_partition_external_id", table_name=_T)
    op.drop_table(_T)
