# -*- coding: utf-8 -*-
"""PostgreSQL table initialization and shared utilities.

Only imported when ``DB_BACKEND=postgresql``.
"""
from __future__ import print_function

__author__ = "bibow"

import logging
from typing import Any

from .base import Base


def initialize_tables(logger: logging.Logger, db_session: Any, engine: Any = None) -> None:
    """Create all PostgreSQL tables that have been imported.

    Uses SQLAlchemy ``metadata.create_all()`` which is idempotent — it only
    creates tables that don't already exist. After table creation, Row-Level
    Security policies are applied to all partition-keyed tables.
    """
    _import_all_models()

    if engine is None:
        engine = db_session.get_bind()

    Base.metadata.create_all(bind=engine, checkfirst=True)
    logger.info("PostgreSQL tables initialized (create_all with checkfirst=True).")

    # Apply Row-Level Security policies on all partition-keyed tables.
    try:
        from ...utils.rls import create_rls_policies

        create_rls_policies(engine)
        logger.info("PostgreSQL RLS policies applied to partition-keyed tables.")
    except Exception as e:
        logger.warning(f"RLS policy creation skipped: {e}")


def _import_all_models() -> None:
    """Import all PostgreSQL model modules to register them with Base.metadata."""
    model_modules = [
        ".place",
        ".corporation_profile",
        ".contact_profile",
        ".contact_request",
        ".attribute_value",
        ".activity_history",
    ]
    for mod_name in model_modules:
        try:
            __import__(
                f"ai_marketing_engine.models.postgresql{mod_name}",
                fromlist=["x"],
            )
        except ImportError:
            _logger = logging.getLogger(__name__)
            _logger.debug(f"PostgreSQL model not yet available: {mod_name}")


__all__ = ["initialize_tables"]
