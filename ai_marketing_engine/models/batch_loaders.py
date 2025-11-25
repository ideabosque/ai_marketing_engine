#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from functools import lru_cache
from typing import Any, Dict, Iterable, List, Optional, Tuple

from promise import Promise
from promise.dataloader import DataLoader

from silvaengine_utility import Utility
from silvaengine_utility.cache import HybridCacheEngine

from ..handlers.config import Config

# Type aliases for readability
Key = Tuple[str, str]


def _normalize_model(model: Any) -> Dict[str, Any]:
    """Safely convert a Pynamo model into a plain dict."""
    return Utility.json_normalize(model.__dict__["attribute_values"])


class _SafeDataLoader(DataLoader):
    """
    Base DataLoader that swallows and logs errors rather than breaking the entire
    request. This keeps individual load failures isolated.
    """

    def __init__(self, logger=None, cache_enabled=True, **kwargs):
        super(_SafeDataLoader, self).__init__(**kwargs)
        self.logger = logger
        self.cache_enabled = cache_enabled and Config.is_cache_enabled()

    def dispatch(self):
        try:
            return super(_SafeDataLoader, self).dispatch()
        except Exception as exc:  # pragma: no cover - defensive
            if self.logger:
                self.logger.exception(exc)
            raise


class PlaceLoader(_SafeDataLoader):
    """Batch loader for PlaceModel records keyed by (endpoint_id, place_uuid)."""

    def __init__(self, logger=None, cache_enabled=True, **kwargs):
        super(PlaceLoader, self).__init__(logger=logger, cache_enabled=cache_enabled, **kwargs)
        if self.cache_enabled:
            self.cache = HybridCacheEngine(Config.get_cache_name("models", "place"))

    def batch_load_fn(self, keys: List[Key]) -> Promise:
        from .place import PlaceModel  # Import locally to avoid circular dependency

        unique_keys = list(dict.fromkeys(keys))
        key_map: Dict[Key, Dict[str, Any]] = {}
        uncached_keys = []

        # Check cache first if enabled
        if self.cache_enabled:
            for key in unique_keys:
                cache_key = f"{key[0]}:{key[1]}"  # endpoint_id:place_uuid
                cached_item = self.cache.get(cache_key)
                if cached_item:
                    key_map[key] = cached_item
                else:
                    uncached_keys.append(key)
        else:
            uncached_keys = unique_keys

        # Batch fetch uncached items
        if uncached_keys:
            try:
                for item in PlaceModel.batch_get(uncached_keys):
                    normalized = _normalize_model(item)
                    key = (item.endpoint_id, item.place_uuid)
                    key_map[key] = normalized
                    
                    # Cache the result if enabled
                    if self.cache_enabled:
                        cache_key = f"{key[0]}:{key[1]}"
                        self.cache.set(cache_key, normalized, ttl=Config.get_cache_ttl())
                        
            except Exception as exc:  # pragma: no cover - defensive
                if self.logger:
                    self.logger.exception(exc)



        return Promise.resolve([key_map.get(key) for key in keys])


class CorporationProfileLoader(_SafeDataLoader):
    """Batch loader for CorporationProfileModel keyed by (endpoint_id, corporation_uuid)."""

    def __init__(self, logger=None, cache_enabled=True, **kwargs):
        super(CorporationProfileLoader, self).__init__(logger=logger, cache_enabled=cache_enabled, **kwargs)
        if self.cache_enabled:
            self.cache = HybridCacheEngine(Config.get_cache_name("models", "corporation_profile"))

    def batch_load_fn(self, keys: List[Key]) -> Promise:
        from .corporation_profile import CorporationProfileModel  # Import locally to avoid circular dependency

        unique_keys = list(dict.fromkeys(keys))
        key_map: Dict[Key, Dict[str, Any]] = {}
        uncached_keys = []

        # Check cache first if enabled
        if self.cache_enabled:
            for key in unique_keys:
                cache_key = f"{key[0]}:{key[1]}"  # endpoint_id:corporation_uuid
                cached_item = self.cache.get(cache_key)
                if cached_item:
                    key_map[key] = cached_item
                else:
                    uncached_keys.append(key)
        else:
            uncached_keys = unique_keys

        # Batch fetch uncached items
        if uncached_keys:
            try:
                for item in CorporationProfileModel.batch_get(uncached_keys):
                    normalized = _normalize_model(item)
                    key = (item.endpoint_id, item.corporation_uuid)
                    key_map[key] = normalized
                    
                    # Cache the result if enabled
                    if self.cache_enabled:
                        cache_key = f"{key[0]}:{key[1]}"
                        self.cache.set(cache_key, normalized, ttl=Config.get_cache_ttl())
                        
            except Exception as exc:  # pragma: no cover - defensive
                if self.logger:
                    self.logger.exception(exc)



        return Promise.resolve([key_map.get(key) for key in keys])


class ContactProfileLoader(_SafeDataLoader):
    """Batch loader for ContactProfileModel keyed by (endpoint_id, contact_uuid)."""

    def __init__(self, logger=None, cache_enabled=True, **kwargs):
        super(ContactProfileLoader, self).__init__(logger=logger, cache_enabled=cache_enabled, **kwargs)
        if self.cache_enabled:
            self.cache = HybridCacheEngine(Config.get_cache_name("models", "contact_profile"))

    def batch_load_fn(self, keys: List[Key]) -> Promise:
        from .contact_profile import ContactProfileModel  # Import locally to avoid circular dependency

        unique_keys = list(dict.fromkeys(keys))
        key_map: Dict[Key, Dict[str, Any]] = {}
        uncached_keys = []

        # Check cache first if enabled
        if self.cache_enabled:
            for key in unique_keys:
                cache_key = f"{key[0]}:{key[1]}"  # endpoint_id:contact_uuid
                cached_item = self.cache.get(cache_key)
                if cached_item:
                    key_map[key] = cached_item
                else:
                    uncached_keys.append(key)
        else:
            uncached_keys = unique_keys

        # Batch fetch uncached items
        if uncached_keys:
            try:
                for item in ContactProfileModel.batch_get(uncached_keys):
                    normalized = _normalize_model(item)
                    key = (item.endpoint_id, item.contact_uuid)
                    key_map[key] = normalized
                    
                    # Cache the result if enabled
                    if self.cache_enabled:
                        cache_key = f"{key[0]}:{key[1]}"
                        self.cache.set(cache_key, normalized, ttl=Config.get_cache_ttl())
                        
            except Exception as exc:  # pragma: no cover - defensive
                if self.logger:
                    self.logger.exception(exc)



        return Promise.resolve([key_map.get(key) for key in keys])


class AttributeDataLoader(_SafeDataLoader):
    """
    Loader for dynamic attribute bags stored in AttributeValueModel.
    Still executes one query per identity, but deduplicates requests within a GraphQL
    execution and caches responses.
    """

    def __init__(self, data_type: str, logger=None, cache_enabled=True, **kwargs):
        super(AttributeDataLoader, self).__init__(logger=logger, cache_enabled=cache_enabled, **kwargs)
        self.data_type = data_type
        if self.cache_enabled:
            self.cache = HybridCacheEngine(Config.get_cache_name("models", f"attribute_{data_type}"))

    @lru_cache(maxsize=128)  # In-memory cache for request scope
    def _get_cached_data(self, endpoint_id: str, data_identity: str) -> Optional[Dict[str, Any]]:
        if not self.cache_enabled:
            return None
        cache_key = f"{endpoint_id}:{data_identity}:{self.data_type}"
        return self.cache.get(cache_key)

    def batch_load_fn(self, keys: List[Key]) -> Promise:
        from .utils import _get_data  # Import locally to avoid circular dependency

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
                
                # Cache the result if enabled
                if self.cache_enabled:
                    cache_key = f"{endpoint_id}:{data_identity}:{self.data_type}"
                    self.cache.set(cache_key, data, ttl=Config.get_cache_ttl())
                    
            except Exception as exc:  # pragma: no cover - defensive
                if self.logger:
                    self.logger.exception(exc)
                results.append(None)



        return Promise.resolve(results)


class RequestLoaders:
    """Container for all DataLoaders scoped to a single GraphQL request."""

    def __init__(self, context: Dict[str, Any], cache_enabled: bool = True):
        logger = context.get("logger")
        self.cache_enabled = cache_enabled
        
        self.place_loader = PlaceLoader(logger=logger, cache_enabled=cache_enabled)
        self.corporation_loader = CorporationProfileLoader(logger=logger, cache_enabled=cache_enabled)
        self.contact_profile_loader = ContactProfileLoader(logger=logger, cache_enabled=cache_enabled)
        self.contact_data_loader = AttributeDataLoader(
            data_type="contact", logger=logger, cache_enabled=cache_enabled
        )
        self.corporation_data_loader = AttributeDataLoader(
            data_type="corporation", logger=logger, cache_enabled=cache_enabled
        )
    
    def invalidate_cache(self, entity_type: str, entity_keys: Dict[str, str]):
        """Invalidate specific cache entries when entities are modified."""
        if not self.cache_enabled:
            return
            
        if entity_type == "place" and "place_uuid" in entity_keys:
            cache_key = f"{entity_keys.get('endpoint_id')}:{entity_keys['place_uuid']}"
            if hasattr(self.place_loader, 'cache'):
                self.place_loader.cache.delete(cache_key)
        elif entity_type == "corporation_profile" and "corporation_uuid" in entity_keys:
            cache_key = f"{entity_keys.get('endpoint_id')}:{entity_keys['corporation_uuid']}"
            if hasattr(self.corporation_loader, 'cache'):
                self.corporation_loader.cache.delete(cache_key)
        elif entity_type == "contact_profile" and "contact_uuid" in entity_keys:
            cache_key = f"{entity_keys.get('endpoint_id')}:{entity_keys['contact_uuid']}"
            if hasattr(self.contact_profile_loader, 'cache'):
                self.contact_profile_loader.cache.delete(cache_key)


def get_loaders(context: Dict[str, Any]) -> RequestLoaders:
    """Fetch or initialize request-scoped loaders from the GraphQL context."""
    if context is None:
        context = {}

    loaders = context.get("batch_loaders")
    if not loaders:
        # Check if caching is enabled
        cache_enabled = Config.is_cache_enabled()
        loaders = RequestLoaders(context, cache_enabled=cache_enabled)
        context["batch_loaders"] = loaders
    return loaders


def clear_loaders(context: Dict[str, Any]) -> None:
    """Clear loaders from context (useful for tests)."""
    if context is None:
        return
    context.pop("batch_loaders", None)
