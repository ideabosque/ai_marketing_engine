# -*- coding: utf-8 -*-
"""Shared helpers for PostgreSQL repositories."""
from __future__ import print_function

__author__ = "bibow"

import logging
import uuid
from typing import Any, Optional, Tuple

from ...postgresql.base import normalize_row


def _normalize(row: Any):
    """Convert a SQLAlchemy ORM row to a normalized dict."""
    return normalize_row(row)


def _get_logger(info: Any) -> logging.Logger:
    try:
        ctx = getattr(info, "context", None) or {}
        return ctx.get("logger") or logging.getLogger()
    except Exception:
        return logging.getLogger()


def _get_partition_key(info: Any) -> Optional[str]:
    try:
        ctx = getattr(info, "context", None) or {}
        return ctx.get("partition_key")
    except Exception:
        return None


def _context_value(info: Any, key: str) -> Optional[Any]:
    try:
        ctx = getattr(info, "context", None) or {}
        return ctx.get(key)
    except Exception:
        return None


def _gen_range_key() -> str:
    """Generate a 20-digit numeric id, matching the DynamoDB decorator."""
    return f"{uuid.uuid1().int % (10**20):020d}"


def _apply_pagination(query: Any, page_number: int, limit: int) -> Tuple[Any, int, int]:
    """Apply offset/limit pagination to a SQLAlchemy query."""
    page_number = max(1, int(page_number or 1))
    limit = max(1, int(limit or 10))
    offset = (page_number - 1) * limit
    return query.offset(offset).limit(limit), offset, limit


__all__ = [
    "_normalize",
    "_get_logger",
    "_get_partition_key",
    "_context_value",
    "_gen_range_key",
    "_apply_pagination",
]
