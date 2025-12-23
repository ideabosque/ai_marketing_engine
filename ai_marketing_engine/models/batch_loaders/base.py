#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from promise.dataloader import DataLoader
from silvaengine_utility.serializer import Serializer

from ...handlers.config import Config

KeyMap = Dict[Any, Any]


def normalize_model(model: Any) -> Dict[str, Any]:
    """
    Safely convert a Pynamo model or pre-normalized dict into a plain dict.
    """
    if model is None:
        return {}

    if isinstance(model, dict):
        return Serializer.json_normalize(model)

    attribute_values = getattr(model, "__dict__", {}).get("attribute_values")
    return Serializer.json_normalize(attribute_values or model)


class SafeDataLoader(DataLoader):
    """
    Base DataLoader that swallows and logs errors rather than breaking the entire
    request. This keeps individual load failures isolated.
    """

    def __init__(self, logger=None, cache_enabled=True, **kwargs):
        super(SafeDataLoader, self).__init__(**kwargs)
        self.logger = logger
        self.cache_enabled = cache_enabled and Config.is_cache_enabled()

    def dispatch(self):
        try:
            return super(SafeDataLoader, self).dispatch()
        except Exception as exc:  # pragma: no cover - defensive
            if self.logger:
                self.logger.exception(exc)
            raise
