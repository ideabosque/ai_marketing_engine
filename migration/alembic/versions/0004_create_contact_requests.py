# -*- coding: utf-8 -*-
"""Create contact_requests table (partition-keyed)

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-16 00:04:00.000000
"""
from __future__ import print_function

__author__ = "bibow"

import os

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

_PREFIX = os.environ.get("PG_TABLE_PREFIX", "ame_")
_T = f"{_PREFIX}contact_requests"


def upgrade() -> None:
    op.create_table(
        _T,
        sa.Column("partition_key", sa.String(128), primary_key=True),
        sa.Column("request_uuid", sa.String(), primary_key=True),
        sa.Column("contact_uuid", sa.String(), nullable=False),
        sa.Column("place_uuid", sa.String(), nullable=True),
        sa.Column("endpoint_id", sa.String(64), nullable=True),
        sa.Column("part_id", sa.String(64), nullable=True),
        sa.Column("request_title", sa.Text(), nullable=True),
        sa.Column("request_detail", sa.Text(), nullable=True),
        sa.Column("updated_by", sa.String(64), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index(f"{_PREFIX}idx_contact_requests_partition_place_uuid", _T, ["partition_key", "place_uuid"])
    op.create_index(f"{_PREFIX}idx_contact_requests_partition_contact_uuid", _T, ["partition_key", "contact_uuid"])


def downgrade() -> None:
    op.drop_index(f"{_PREFIX}idx_contact_requests_partition_contact_uuid", table_name=_T)
    op.drop_index(f"{_PREFIX}idx_contact_requests_partition_place_uuid", table_name=_T)
    op.drop_table(_T)
