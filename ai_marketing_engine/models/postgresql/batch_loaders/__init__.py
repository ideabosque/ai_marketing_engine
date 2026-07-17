# -*- coding: utf-8 -*-
"""PGRequestLoaders — PostgreSQL DataLoader container.

Property names match the DynamoDB ``RequestLoaders`` exactly so that the
nested-type resolvers in ``types/*`` work unchanged across both backends:
``place_loader``, ``corporation_loader``, ``contact_profile_loader``,
``contact_data_loader``, ``corporation_data_loader``.
"""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict


class PGRequestLoaders:
    """Request-scoped PostgreSQL DataLoader container."""

    def __init__(self, context: Dict[str, Any], cache_enabled: bool = True) -> None:
        self._context = context or {}
        self._cache_enabled = cache_enabled

        from .attribute_data_loader import AttributeDataLoader
        from .contact_profile_loader import ContactProfileLoader
        from .corporation_profile_loader import CorporationProfileLoader
        from .place_loader import PlaceLoader

        self.place_loader = PlaceLoader(self._context, cache_enabled=cache_enabled)
        self.corporation_loader = CorporationProfileLoader(
            self._context, cache_enabled=cache_enabled
        )
        self.contact_profile_loader = ContactProfileLoader(
            self._context, cache_enabled=cache_enabled
        )
        self.contact_data_loader = AttributeDataLoader(
            self._context, data_type="contact", cache_enabled=cache_enabled
        )
        self.corporation_data_loader = AttributeDataLoader(
            self._context, data_type="corporation", cache_enabled=cache_enabled
        )

    def invalidate_cache(self, entity_type: str, entity_keys: Dict[str, str]) -> None:
        """No-op: PG loaders are request-scoped in-memory caches only."""
        return None


__all__ = ["PGRequestLoaders"]
