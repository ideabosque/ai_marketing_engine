#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo
from silvaengine_utility import method_cache

from ..handlers.config import Config
from ..models import attribute_value
from ..types.attribute_value import AttributeValueListType, AttributeValueType


def resolve_attribute_value(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> AttributeValueType | None:
    return attribute_value.resolve_attribute_value(info, **kwargs)


@method_cache(
    ttl=Config.get_cache_ttl(),
    cache_name=Config.get_cache_name("queries", "attribute_value"),
    cache_enabled=Config.is_cache_enabled,
)
def resolve_attribute_value_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> AttributeValueListType:
    return attribute_value.resolve_attribute_value_list(info, **kwargs)
