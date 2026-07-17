# -*- coding: utf-8 -*-
"""SafeDataLoader for PostgreSQL — batch loading with error isolation.

Mirrors the contract of the DynamoDB batch loaders:
- Subclasses implement ``_batch_load_fn(keys) -> Dict[key, normalized_dict|None]``
- ``.load(key)`` returns a Promise that resolves to the value or None
- Individual key errors are isolated (one bad key doesn't break the batch)
- Results are cached per-loader-instance (request-scoped)
"""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, List, Optional

from promise import Promise


class SafeDataLoader:
    """Base class for PostgreSQL DataLoaders with error isolation."""

    def __init__(self, context: Dict[str, Any], cache_enabled: bool = True) -> None:
        self._context = context or {}
        self.logger = self._context.get("logger")
        self._cache_enabled = cache_enabled
        self._cache: Dict[Any, Any] = {}
        self._batch: Dict[Any, Any] = {}
        self._scheduled: bool = False

    def _batch_load_fn(self, keys: List[Any]) -> Dict[Any, Optional[Dict[str, Any]]]:
        """Override: map each key to a normalized row dict (or None)."""
        raise NotImplementedError("Subclasses must implement _batch_load_fn")

    def load(self, key: Any) -> Promise:
        """Queue a key for batch loading and return a Promise."""
        if self._cache_enabled and key in self._cache:
            return Promise.resolve(self._cache[key])

        if key in self._batch:
            return self._batch[key][0]

        resolver_holder: Dict[str, Any] = {}

        def _executor(resolve, reject):
            resolver_holder["resolve"] = resolve
            resolver_holder["reject"] = reject

        promise = Promise(_executor)
        self._batch[key] = (promise, resolver_holder)

        if not self._scheduled:
            self._scheduled = True
            import asyncio

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.call_soon(self._dispatch_batch)
                else:
                    self._dispatch_batch()
            except RuntimeError:
                self._dispatch_batch()

        return promise

    def load_many(self, keys: List[Any]) -> Promise:
        return Promise.all([self.load(key) for key in keys])

    def _dispatch_batch(self) -> None:
        self._scheduled = False
        keys = list(self._batch.keys())
        if not keys:
            return

        entries = {k: self._batch.pop(k) for k in keys}
        try:
            results = self._batch_load_fn(keys)
            for key in keys:
                val = results.get(key)
                if self._cache_enabled:
                    self._cache[key] = val
                entries[key][1]["resolve"](val)
        except Exception as exc:
            if self.logger:
                self.logger.exception(exc)
            for key in keys:
                entries[key][1]["reject"](exc)

    def clear(self, key: Any) -> None:
        self._cache.pop(key, None)

    def clear_all(self) -> None:
        self._cache.clear()


__all__ = ["SafeDataLoader"]
