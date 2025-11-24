#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, Iterable, List, Optional, Tuple

from promise import Promise
from promise.dataloader import DataLoader

from silvaengine_utility import Utility

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

    def __init__(self, logger=None, **kwargs):
        super(_SafeDataLoader, self).__init__(**kwargs)
        self.logger = logger

    def dispatch(self):
        try:
            return super(_SafeDataLoader, self).dispatch()
        except Exception as exc:  # pragma: no cover - defensive
            if self.logger:
                self.logger.exception(exc)
            raise


class PlaceLoader(_SafeDataLoader):
    """Batch loader for PlaceModel records keyed by (endpoint_id, place_uuid)."""

    def batch_load_fn(self, keys: List[Key]) -> Promise:
        from .place import PlaceModel  # Import locally to avoid circular dependency

        unique_keys = list(dict.fromkeys(keys))
        key_map: Dict[Key, Dict[str, Any]] = {}

        try:
            for item in PlaceModel.batch_get(unique_keys):
                key_map[(item.endpoint_id, item.place_uuid)] = _normalize_model(item)
        except Exception as exc:  # pragma: no cover - defensive
            if self.logger:
                self.logger.exception(exc)

        return Promise.resolve([key_map.get(key) for key in keys])


class CorporationProfileLoader(_SafeDataLoader):
    """Batch loader for CorporationProfileModel keyed by (endpoint_id, corporation_uuid)."""

    def batch_load_fn(self, keys: List[Key]) -> Promise:
        from .corporation_profile import CorporationProfileModel  # Import locally to avoid circular dependency

        unique_keys = list(dict.fromkeys(keys))
        key_map: Dict[Key, Dict[str, Any]] = {}

        try:
            for item in CorporationProfileModel.batch_get(unique_keys):
                key_map[(item.endpoint_id, item.corporation_uuid)] = _normalize_model(
                    item
                )
        except Exception as exc:  # pragma: no cover - defensive
            if self.logger:
                self.logger.exception(exc)

        return Promise.resolve([key_map.get(key) for key in keys])


class ContactProfileLoader(_SafeDataLoader):
    """Batch loader for ContactProfileModel keyed by (endpoint_id, contact_uuid)."""

    def batch_load_fn(self, keys: List[Key]) -> Promise:
        from .contact_profile import ContactProfileModel  # Import locally to avoid circular dependency

        unique_keys = list(dict.fromkeys(keys))
        key_map: Dict[Key, Dict[str, Any]] = {}

        try:
            for item in ContactProfileModel.batch_get(unique_keys):
                key_map[(item.endpoint_id, item.contact_uuid)] = _normalize_model(item)
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

    def __init__(self, data_type: str, logger=None, **kwargs):
        super(AttributeDataLoader, self).__init__(logger=logger, **kwargs)
        self.data_type = data_type

    def batch_load_fn(self, keys: List[Key]) -> Promise:
        from .utils import _get_data  # Import locally to avoid circular dependency

        cache: Dict[Key, Dict[str, Any]] = {}
        results: List[Optional[Dict[str, Any]]] = []

        for endpoint_id, data_identity in keys:
            key = (endpoint_id, data_identity)
            if key not in cache:
                try:
                    cache[key] = _get_data(endpoint_id, data_identity, self.data_type)
                except Exception as exc:  # pragma: no cover - defensive
                    if self.logger:
                        self.logger.exception(exc)
                    cache[key] = None
            results.append(cache.get(key))

        return Promise.resolve(results)


class RequestLoaders:
    """Container for all DataLoaders scoped to a single GraphQL request."""

    def __init__(self, context: Dict[str, Any]):
        logger = context.get("logger")
        self.place_loader = PlaceLoader(logger=logger)
        self.corporation_loader = CorporationProfileLoader(logger=logger)
        self.contact_profile_loader = ContactProfileLoader(logger=logger)
        self.contact_data_loader = AttributeDataLoader(
            data_type="contact", logger=logger
        )
        self.corporation_data_loader = AttributeDataLoader(
            data_type="corporation", logger=logger
        )


def get_loaders(context: Dict[str, Any]) -> RequestLoaders:
    """Fetch or initialize request-scoped loaders from the GraphQL context."""
    if context is None:
        context = {}

    loaders = context.get("batch_loaders")
    if not loaders:
        loaders = RequestLoaders(context)
        context["batch_loaders"] = loaders
    return loaders


def clear_loaders(context: Dict[str, Any]) -> None:
    """Clear loaders from context (useful for tests)."""
    if context is None:
        return
    context.pop("batch_loaders", None)
