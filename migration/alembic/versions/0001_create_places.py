# -*- coding: utf-8 -*-
"""Create places table (partition-keyed)

Revision ID: 0001
Revises:
Create Date: 2026-07-16 00:01:00.000000
"""
from __future__ import print_function

__author__ = "bibow"

import os

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

_PREFIX = os.environ.get("PG_TABLE_PREFIX", "ame_")
_T = f"{_PREFIX}places"


def upgrade() -> None:
    op.create_table(
        _T,
        sa.Column("partition_key", sa.String(128), primary_key=True),
        sa.Column("place_uuid", sa.String(), primary_key=True),
        sa.Column("endpoint_id", sa.String(64), nullable=True),
        sa.Column("part_id", sa.String(64), nullable=True),
        sa.Column("region", sa.String(), nullable=True),
        sa.Column("latitude", sa.String(), nullable=True),
        sa.Column("longitude", sa.String(), nullable=True),
        sa.Column("business_name", sa.Text(), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("phone_number", sa.String(), nullable=True),
        sa.Column("website", sa.String(), nullable=True),
        sa.Column("types", postgresql.JSONB, nullable=True),
        sa.Column("corporation_uuid", sa.String(), nullable=True),
        sa.Column("updated_by", sa.String(64), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index(f"{_PREFIX}idx_places_partition_region", _T, ["partition_key", "region"])
    op.create_index(f"{_PREFIX}idx_places_partition_corporation_uuid", _T, ["partition_key", "corporation_uuid"])


def downgrade() -> None:
    op.drop_index(f"{_PREFIX}idx_places_partition_corporation_uuid", table_name=_T)
    op.drop_index(f"{_PREFIX}idx_places_partition_region", table_name=_T)
    op.drop_table(_T)
