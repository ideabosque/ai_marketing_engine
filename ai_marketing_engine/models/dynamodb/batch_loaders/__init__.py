#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from silvaengine_utility.cache import HybridCacheEngine

from ....handlers.config import Config
from .attribute_data_loader import AttributeDataLoader
from .contact_profile_loader import ContactProfileLoader
from .corporation_profile_loader import CorporationProfileLoader
from .place_loader import PlaceLoader


class RequestLoaders:
    """Container for all DynamoDB DataLoaders scoped to a single GraphQL request."""

    def __init__(self, context: Dict[str, Any], cache_enabled: bool = True):
        logger = context.get("logger")
        self.cache_enabled = cache_enabled

        self.place_loader = PlaceLoader(logger=logger, cache_enabled=cache_enabled)
        self.corporation_loader = CorporationProfileLoader(
            logger=logger, cache_enabled=cache_enabled
        )
        self.contact_profile_loader = ContactProfileLoader(
            logger=logger, cache_enabled=cache_enabled
        )
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
            cache_key = self.place_loader.generate_cache_key(
                (entity_keys.get("endpoint_id"), entity_keys["place_uuid"])
            )
            if hasattr(self.place_loader, "cache"):
                self.place_loader.cache.delete(cache_key)
        elif entity_type == "corporation_profile" and "corporation_uuid" in entity_keys:
            cache_key = self.corporation_loader.generate_cache_key(
                (entity_keys.get("endpoint_id"), entity_keys["corporation_uuid"])
            )
            if hasattr(self.corporation_loader, "cache"):
                self.corporation_loader.cache.delete(cache_key)
        elif entity_type == "contact_profile" and "contact_uuid" in entity_keys:
            cache_key = self.contact_profile_loader.generate_cache_key(
                (entity_keys.get("endpoint_id"), entity_keys["contact_uuid"])
            )
            if hasattr(self.contact_profile_loader, "cache"):
                self.contact_profile_loader.cache.delete(cache_key)


__all__ = [
    "RequestLoaders",
    "HybridCacheEngine",
    "AttributeDataLoader",
    "ContactProfileLoader",
    "CorporationProfileLoader",
    "PlaceLoader",
]
