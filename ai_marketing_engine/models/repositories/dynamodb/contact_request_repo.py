# -*- coding: utf-8 -*-
"""DynamoDB repository for ContactRequest (thin wrapper over model funcs)."""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, Optional

from ...dynamodb.contact_request import (
    delete_contact_request,
    get_contact_request,
    get_contact_request_count,
    get_contact_request_type,
    insert_update_contact_request,
    resolve_contact_request,
    resolve_contact_request_list,
)
from ..base import EntityRepository
from ._base import _normalize


class ContactRequestRepository(EntityRepository):
    """DynamoDB repository for ContactRequest."""

    @property
    def entity_type(self) -> str:
        return "contact_request"

    def get(self, **keys: Any) -> Optional[Dict[str, Any]]:
        partition_key = keys.get("partition_key")
        request_uuid = keys.get("request_uuid")
        if not partition_key or not request_uuid:
            return None
        if get_contact_request_count(partition_key, request_uuid) == 0:
            return None
        return _normalize(get_contact_request(partition_key, request_uuid))

    def count(self, **keys: Any) -> int:
        partition_key = keys.get("partition_key")
        request_uuid = keys.get("request_uuid")
        if not partition_key or not request_uuid:
            return 0
        return get_contact_request_count(partition_key, request_uuid)

    def list(self, info: Any, **filters: Any) -> Any:
        return resolve_contact_request_list(info, **filters)

    def insert_update(self, info: Any, **kwargs: Any) -> Any:
        return insert_update_contact_request(info, **kwargs)

    def delete(self, info: Any, **kwargs: Any) -> bool:
        return delete_contact_request(info, **kwargs)

    def resolve_single(self, info: Any, **kwargs: Any) -> Any:
        return resolve_contact_request(info, **kwargs)

    def get_type(self, info: Any, instance: Any) -> Any:
        return get_contact_request_type(info, instance)


__all__ = ["ContactRequestRepository"]
