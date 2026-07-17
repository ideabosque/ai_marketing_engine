# -*- coding: utf-8 -*-
"""PostgreSQL DataLoader for PlaceModel keyed by (partition_key, place_uuid)."""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, List, Optional, Tuple

from .base import SafeDataLoader

Key = Tuple[str, str]


class PlaceLoader(SafeDataLoader):
    """Batch loader for PlaceModel records keyed by (partition_key, place_uuid)."""

    def _batch_load_fn(self, keys: List[Key]) -> Dict[Key, Optional[Dict[str, Any]]]:
        from ....handlers.config import Config
        from ...postgresql.base import normalize_row
        from ...postgresql.place import PlaceModel

        unique_keys = list(dict.fromkeys(keys))
        partition_keys = {pk for pk, _ in unique_keys}
        place_uuids = {pu for _, pu in unique_keys}

        session = Config.db_session()
        try:
            rows = (
                session.query(PlaceModel)
                .filter(
                    PlaceModel.partition_key.in_(partition_keys),
                    PlaceModel.place_uuid.in_(place_uuids),
                )
                .all()
            )
        except Exception:
            session.rollback()
            raise

        key_map: Dict[Key, Optional[Dict[str, Any]]] = {}
        for row in rows:
            key_map[(row.partition_key, row.place_uuid)] = normalize_row(row)

        return {key: key_map.get(key) for key in keys}


__all__ = ["PlaceLoader"]
