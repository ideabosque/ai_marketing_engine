# -*- coding: utf-8 -*-
"""DynamoDB repository for CorporationProfile (thin wrapper over model funcs)."""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, Optional

from ...dynamodb.corporation_profile import (
    delete_corporation_profile,
    get_corporation_profile,
    get_corporation_profile_count,
    get_corporation_profile_type,
    insert_update_corporation_profile,
    resolve_corporation_profile,
    resolve_corporation_profile_list,
)
from ..base import EntityRepository
from ._base import _normalize


class CorporationProfileRepository(EntityRepository):
    """DynamoDB repository for CorporationProfile."""

    @property
    def entity_type(self) -> str:
        return "corporation_profile"

    def get(self, **keys: Any) -> Optional[Dict[str, Any]]:
        partition_key = keys.get("partition_key")
        corporation_uuid = keys.get("corporation_uuid")
        if not partition_key or not corporation_uuid:
            return None
        if get_corporation_profile_count(partition_key, corporation_uuid) == 0:
            return None
        return _normalize(get_corporation_profile(partition_key, corporation_uuid))

    def count(self, **keys: Any) -> int:
        partition_key = keys.get("partition_key")
        corporation_uuid = keys.get("corporation_uuid")
        if not partition_key or not corporation_uuid:
            return 0
        return get_corporation_profile_count(partition_key, corporation_uuid)

    def list(self, info: Any, **filters: Any) -> Any:
        return resolve_corporation_profile_list(info, **filters)

    def insert_update(self, info: Any, **kwargs: Any) -> Any:
        return insert_update_corporation_profile(info, **kwargs)

    def delete(self, info: Any, **kwargs: Any) -> bool:
        return delete_corporation_profile(info, **kwargs)

    def resolve_single(self, info: Any, **kwargs: Any) -> Any:
        return resolve_corporation_profile(info, **kwargs)

    def get_type(self, info: Any, instance: Any) -> Any:
        return get_corporation_profile_type(info, instance)


__all__ = ["CorporationProfileRepository"]
