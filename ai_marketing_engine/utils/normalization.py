# -*- coding: utf-8 -*-
"""Normalization helpers shared by both persistence backends.

``normalize_to_json`` converts PynamoDB models, SQLAlchemy rows, or plain
objects into JSON-serializable dictionaries so nothing backend-specific
leaks above the repository boundary.
"""
from __future__ import print_function

__author__ = "bibow"

from typing import Any

from silvaengine_utility import Serializer


def normalize_to_json(item: Any) -> Any:
    """Convert model objects or plain objects into JSON-serializable data."""
    if isinstance(item, dict):
        return Serializer.json_normalize(item)
    if hasattr(item, "attribute_values"):
        return Serializer.json_normalize(item.attribute_values)
    if hasattr(item, "__dict__"):
        return Serializer.json_normalize(
            {k: v for k, v in vars(item).items() if not k.startswith("_")}
        )
    return item


__all__ = ["normalize_to_json"]
