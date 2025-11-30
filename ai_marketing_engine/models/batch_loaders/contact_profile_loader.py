#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, List, Tuple

from promise import Promise
from silvaengine_utility.cache import HybridCacheEngine

from ...handlers.config import Config
from ..contact_profile import ContactProfileModel
from .base import SafeDataLoader, normalize_model

Key = Tuple[str, str]


class ContactProfileLoader(SafeDataLoader):
    """Batch loader for ContactProfileModel keyed by (endpoint_id, contact_uuid)."""

    def __init__(self, logger=None, cache_enabled=True, **kwargs):
        super(ContactProfileLoader, self).__init__(
            logger=logger, cache_enabled=cache_enabled, **kwargs
        )
        if self.cache_enabled:
            self.cache = HybridCacheEngine(
                Config.get_cache_name("models", "contact_profile")
            )

    @staticmethod
    def _cache_key(endpoint_id: str, contact_uuid: str) -> str:
        return f"{endpoint_id}:{contact_uuid}"

    def batch_load_fn(self, keys: List[Key]) -> Promise:
        unique_keys = list(dict.fromkeys(keys))
        key_map: Dict[Key, Dict[str, Any]] = {}
        uncached_keys = []

        # Check cache first if enabled
        if self.cache_enabled:
            for endpoint_id, contact_uuid in unique_keys:
                cache_key = self._cache_key(endpoint_id, contact_uuid)
                cached_item = self.cache.get(cache_key)
                if cached_item:
                    key_map[(endpoint_id, contact_uuid)] = cached_item
                else:
                    uncached_keys.append((endpoint_id, contact_uuid))
        else:
            uncached_keys = unique_keys

        # Batch fetch uncached items
        if uncached_keys:
            try:
                for item in ContactProfileModel.batch_get(uncached_keys):
                    key = (item.endpoint_id, item.contact_uuid)
                    normalized = normalize_model(item)
                    key_map[key] = normalized

                    if self.cache_enabled:
                        cache_key = self._cache_key(*key)
                        self.cache.set(cache_key, normalized, ttl=Config.get_cache_ttl())

            except Exception as exc:  # pragma: no cover - defensive
                if self.logger:
                    self.logger.exception(exc)

        return Promise.resolve([key_map.get(key) for key in keys])
