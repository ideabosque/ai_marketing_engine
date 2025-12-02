#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, List, Optional, Tuple

from promise import Promise
from silvaengine_utility.cache import HybridCacheEngine

from ...handlers.config import Config
from .base import SafeDataLoader

Key = Tuple[str, str]


class AttributeDataLoader(SafeDataLoader):
    """
    Loader for dynamic attribute bags stored in AttributeValueModel.
    Still executes one query per identity, but deduplicates requests within a GraphQL
    execution and caches responses.
    """

    def __init__(self, data_type: str, logger=None, cache_enabled=True, **kwargs):
        super(AttributeDataLoader, self).__init__(
            logger=logger, cache_enabled=cache_enabled, **kwargs
        )
        self.data_type = data_type
        if self.cache_enabled:
            self.cache = HybridCacheEngine(
                Config.get_cache_name("models", "attributes_data")
            )
            cache_meta = Config.get_cache_entity_config().get("attributes_data")
            self.cache_func_prefix = ""
            if cache_meta:
                self.cache_func_prefix = ".".join([cache_meta.get("module"), cache_meta.get("getter")])

    def generate_cache_key(self, key: Key) -> str:
        key_data = ":".join([str(key), str({})])
        return self.cache._generate_key(
            self.cache_func_prefix,
            key_data
        )
    
    def get_cache_data(self, key: Key) -> Dict[str, Any] | None:
        cache_key = self.generate_cache_key(key)
        cached_item = self.cache.get(cache_key)
        if cached_item is None:  # pragma: no cover - defensive
            return None
        return cached_item

    def set_cache_data(self, key: Key, data: Any) -> None:
        cache_key = self.generate_cache_key(key)
        self.cache.set(cache_key, data, ttl=Config.get_cache_ttl())

    def batch_load_fn(self, keys: List[Key]) -> Promise:
        from ..utils import _get_data  # Import locally to avoid circular dependency

        results: List[Optional[Dict[str, Any]]] = []

        for endpoint_id, data_identity in keys:
            # Check cache first if enabled
            if self.cache_enabled:
                cached_data = self.get_cache_data((endpoint_id, data_identity, self.data_type))
                if cached_data is not None:
                    results.append(cached_data)
                    continue

            # Fetch from database
            try:
                data = _get_data(endpoint_id, data_identity, self.data_type)
                results.append(data)

                if self.cache_enabled:
                    key = (endpoint_id, data_identity, self.data_type)
                    self.set_cache_data(key, data)

            except Exception as exc:  # pragma: no cover - defensive
                if self.logger:
                    self.logger.exception(exc)
                results.append(None)

        return Promise.resolve(results)
