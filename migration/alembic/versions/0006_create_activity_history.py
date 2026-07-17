# -*- coding: utf-8 -*-
"""Create activity_history table (global, no partition_key — not RLS-protected)

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-16 00:06:00.000000
"""
from __future__ import print_function

__author__ = "bibow"

import os

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

_PREFIX = os.environ.get("PG_TABLE_PREFIX", "ame_")
_T = f"{_PREFIX}activity_history"


def upgrade() -> None:
    op.create_table(
        _T,
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("timestamp", sa.BigInteger(), primary_key=True),
        sa.Column("log", sa.Text(), nullable=True),
        sa.Column("data_diff", postgresql.JSONB, nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column("updated_by", sa.String(64), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index(f"{_PREFIX}idx_activity_history_type_id", _T, ["type", "id"])


def downgrade() -> None:
    op.drop_index(f"{_PREFIX}idx_activity_history_type_id", table_name=_T)
    op.drop_table(_T)
