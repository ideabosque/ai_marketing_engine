# -*- coding: utf-8 -*-
"""DynamoDB repository for ContactProfile (thin wrapper over model funcs)."""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, Optional

from ...dynamodb.contact_profile import (
    delete_contact_profile,
    get_contact_profile,
    get_contact_profile_count,
    get_contact_profile_type,
    insert_update_contact_profile,
    resolve_contact_profile,
    resolve_contact_profile_list,
)
from ..base import EntityRepository
from ._base import _normalize


class ContactProfileRepository(EntityRepository):
    """DynamoDB repository for ContactProfile."""

    @property
    def entity_type(self) -> str:
        return "contact_profile"

    def get(self, **keys: Any) -> Optional[Dict[str, Any]]:
        partition_key = keys.get("partition_key")
        contact_uuid = keys.get("contact_uuid")
        if not partition_key or not contact_uuid:
            return None
        if get_contact_profile_count(partition_key, contact_uuid) == 0:
            return None
        return _normalize(get_contact_profile(partition_key, contact_uuid))

    def count(self, **keys: Any) -> int:
        partition_key = keys.get("partition_key")
        contact_uuid = keys.get("contact_uuid")
        if not partition_key or not contact_uuid:
            return 0
        return get_contact_profile_count(partition_key, contact_uuid)

    def list(self, info: Any, **filters: Any) -> Any:
        return resolve_contact_profile_list(info, **filters)

    def insert_update(self, info: Any, **kwargs: Any) -> Any:
        return insert_update_contact_profile(info, **kwargs)

    def delete(self, info: Any, **kwargs: Any) -> bool:
        return delete_contact_profile(info, **kwargs)

    def resolve_single(self, info: Any, **kwargs: Any) -> Any:
        return resolve_contact_profile(info, **kwargs)

    def get_type(self, info: Any, instance: Any) -> Any:
        return get_contact_profile_type(info, instance)


__all__ = ["ContactProfileRepository"]
