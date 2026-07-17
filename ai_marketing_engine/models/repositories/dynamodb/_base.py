# -*- coding: utf-8 -*-
"""Shared helpers for DynamoDB repositories."""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, Optional

from ....utils.normalization import normalize_to_json


def _normalize(model: Any) -> Optional[Dict[str, Any]]:
    """Convert a PynamoDB model instance to a normalized dict."""
    if model is None:
        return None
    return normalize_to_json(model)


__all__ = ["_normalize"]
