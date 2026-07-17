# -*- coding: utf-8 -*-
"""PostgreSQL DataLoader for CorporationProfileModel.

Keyed by (partition_key, corporation_uuid).
"""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, List, Optional, Tuple

from .base import SafeDataLoader

Key = Tuple[str, str]


class CorporationProfileLoader(SafeDataLoader):
    """Batch loader for CorporationProfileModel keyed by (partition_key, corporation_uuid)."""

    def _batch_load_fn(self, keys: List[Key]) -> Dict[Key, Optional[Dict[str, Any]]]:
        from ....handlers.config import Config
        from ...postgresql.base import normalize_row
        from ...postgresql.corporation_profile import CorporationProfileModel

        unique_keys = list(dict.fromkeys(keys))
        partition_keys = {pk for pk, _ in unique_keys}
        corporation_uuids = {cu for _, cu in unique_keys}

        session = Config.db_session()
        try:
            rows = (
                session.query(CorporationProfileModel)
                .filter(
                    CorporationProfileModel.partition_key.in_(partition_keys),
                    CorporationProfileModel.corporation_uuid.in_(corporation_uuids),
                )
                .all()
            )
        except Exception:
            session.rollback()
            raise

        key_map: Dict[Key, Optional[Dict[str, Any]]] = {}
        for row in rows:
            key_map[(row.partition_key, row.corporation_uuid)] = normalize_row(row)

        return {key: key_map.get(key) for key in keys}


__all__ = ["CorporationProfileLoader"]
