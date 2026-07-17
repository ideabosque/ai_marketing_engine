# -*- coding: utf-8 -*-
"""PostgreSQL DataLoader for dynamic attribute bags (AttributeValueModel).

Keyed by (partition_key, data_identity); returns a ``{attribute_name: value}``
dict of the active attribute values for the loader's ``data_type``.
"""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, List, Optional, Tuple

from .base import SafeDataLoader

Key = Tuple[str, str]


class AttributeDataLoader(SafeDataLoader):
    """Loader for dynamic attribute bags stored in AttributeValueModel."""

    def __init__(
        self, context: Dict[str, Any], data_type: str, cache_enabled: bool = True
    ) -> None:
        super(AttributeDataLoader, self).__init__(context, cache_enabled=cache_enabled)
        self.data_type = data_type

    def _batch_load_fn(self, keys: List[Key]) -> Dict[Key, Optional[Dict[str, Any]]]:
        from ....handlers.config import Config
        from ...postgresql.attribute_value import AttributeValueModel

        results: Dict[Key, Optional[Dict[str, Any]]] = {}
        session = Config.db_session()
        try:
            for partition_key, data_identity in keys:
                rows = (
                    session.query(AttributeValueModel)
                    .filter(
                        AttributeValueModel.partition_key == partition_key,
                        AttributeValueModel.data_identity == data_identity,
                        AttributeValueModel.data_type_attribute_name.like(
                            f"{self.data_type}-%"
                        ),
                        AttributeValueModel.status == "active",
                    )
                    .all()
                )
                results[(partition_key, data_identity)] = {
                    row.data_type_attribute_name.split("-", 1)[1]: row.value
                    for row in rows
                }
        except Exception:
            session.rollback()
            raise

        return {key: results.get(key) for key in keys}


__all__ = ["AttributeDataLoader"]
