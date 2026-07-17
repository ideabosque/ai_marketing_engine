# -*- coding: utf-8 -*-
"""Row-Level Security (RLS) helpers for the PostgreSQL backend.

These functions enforce tenant isolation at the database level so that even
if a query forgets to filter on ``partition_key``, PostgreSQL still restricts
rows to the current tenant context.

Only imported when ``DB_BACKEND=postgresql``.

Usage
-----
1. ``set_rls_context(session, partition_key)`` — called at the start of each
   request (and each background/async invocation that opens its own session)
   to set the ``app.tenant_id`` session variable.
2. ``create_rls_policies(engine)`` — called once during table initialization
   to enable RLS and create policies on all partition-keyed tables.
"""
from __future__ import print_function

__author__ = "bibow"

import logging
from typing import Any

from sqlalchemy import text

logger = logging.getLogger(__name__)


# Partition-keyed tables (unprefixed) that participate in tenant isolation.
# ``activity_history`` is intentionally excluded — it has no ``partition_key``
# column (it is a global, id/timestamp-keyed audit log).
_RLS_TABLES = [
    "places",
    "contact_profiles",
    "contact_requests",
    "corporation_profiles",
    "attribute_values",
]


def set_rls_context(session: Any, partition_key: str) -> None:
    """Set the RLS tenant context for the current database session.

    Executes ``SET app.tenant_id = :tenant`` (connection-level, not
    ``SET LOCAL``) so the tenant context survives the ``commit()`` a mutation
    issues before its response's nested resolvers read related rows. The
    scoped session is torn down at the request boundary, and every entry point
    re-sets the context before its first query, so a pooled connection never
    serves another tenant with a stale value.
    """
    if not partition_key:
        raise ValueError("partition_key must be a non-empty string for RLS context.")

    session.execute(
        text("SET app.tenant_id = :tenant"),
        {"tenant": partition_key},
    )


def create_rls_policies(engine: Any) -> None:
    """Enable Row-Level Security and create tenant-isolation policies.

    For each partition-keyed table this runs::

        ALTER TABLE <prefix><table> ENABLE ROW LEVEL SECURITY;
        ALTER TABLE <prefix><table> FORCE ROW LEVEL SECURITY;
        CREATE POLICY tenant_isolation ON <prefix><table>
            USING (partition_key = current_setting('app.tenant_id', true));

    Idempotent: existing policies are dropped before re-creation so the
    function can run on every startup without error.
    """
    from ..models.postgresql.base import prefixed_table

    with engine.connect() as conn:
        for table_name in _RLS_TABLES:
            actual_name = prefixed_table(table_name)
            try:
                conn.execute(
                    text(f"ALTER TABLE {actual_name} ENABLE ROW LEVEL SECURITY")
                )
                conn.execute(
                    text(f"ALTER TABLE {actual_name} FORCE ROW LEVEL SECURITY")
                )
                conn.execute(
                    text(f"DROP POLICY IF EXISTS tenant_isolation ON {actual_name}")
                )
                conn.execute(
                    text(
                        f"CREATE POLICY tenant_isolation ON {actual_name} "
                        f"USING (partition_key = current_setting('app.tenant_id', true))"
                    )
                )
                logger.debug(f"RLS policy applied to {actual_name}")
            except Exception as exc:
                logger.warning(f"Failed to apply RLS to {actual_name}: {exc}")
        conn.commit()


__all__ = ["set_rls_context", "create_rls_policies", "_RLS_TABLES"]
