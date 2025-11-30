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

    def _cache_key(self, endpoint_id: str, data_identity: str) -> str:
        return f"{endpoint_id}:{data_identity}:{self.data_type}"

    def _get_cached_data(self, endpoint_id: str, data_identity: str) -> Optional[Dict[str, Any]]:
        if not self.cache_enabled:
            return None
        return self.cache.get(self._cache_key(endpoint_id, data_identity))

    def batch_load_fn(self, keys: List[Key]) -> Promise:
        from ..utils import _get_data  # Import locally to avoid circular dependency

        results: List[Optional[Dict[str, Any]]] = []

        for endpoint_id, data_identity in keys:
            # Check cache first if enabled
            if self.cache_enabled:
                cached_data = self._get_cached_data(endpoint_id, data_identity)
                if cached_data is not None:
                    results.append(cached_data)
                    continue

            # Fetch from database
            try:
                data = _get_data(endpoint_id, data_identity, self.data_type)
                results.append(data)

                if self.cache_enabled:
                    self.cache.set(
                        self._cache_key(endpoint_id, data_identity),
                        data,
                        ttl=Config.get_cache_ttl(),
                    )

            except Exception as exc:  # pragma: no cover - defensive
                if self.logger:
                    self.logger.exception(exc)
                results.append(None)

        return Promise.resolve(results)
