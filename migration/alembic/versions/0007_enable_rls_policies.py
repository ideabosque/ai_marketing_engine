# -*- coding: utf-8 -*-
"""Enable Row-Level Security policies on all partition-keyed tables.

``activity_history`` is intentionally excluded — it has no ``partition_key``.

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-16 00:07:00.000000
"""
from __future__ import print_function

__author__ = "bibow"

import os

from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None

_PREFIX = os.environ.get("PG_TABLE_PREFIX", "ame_")

RLS_TABLES = [
    "places",
    "contact_profiles",
    "contact_requests",
    "corporation_profiles",
    "attribute_values",
]


def upgrade() -> None:
    for table in RLS_TABLES:
        full_name = f"{_PREFIX}{table}"
        op.execute(f"ALTER TABLE {full_name} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {full_name} FORCE ROW LEVEL SECURITY")
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {full_name}")
        op.execute(
            f"CREATE POLICY tenant_isolation ON {full_name} "
            f"USING (partition_key = current_setting('app.tenant_id', true))"
        )


def downgrade() -> None:
    for table in RLS_TABLES:
        full_name = f"{_PREFIX}{table}"
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {full_name}")
        op.execute(f"ALTER TABLE {full_name} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {full_name} DISABLE ROW LEVEL SECURITY")
