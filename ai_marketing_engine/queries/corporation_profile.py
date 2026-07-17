#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo
from silvaengine_utility import method_cache

from ..handlers.config import Config
from ..models.repositories import get_repo
from ..types.corporation_profile import (
    CorporationProfileListType,
    CorporationProfileType,
)


def resolve_corporation_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CorporationProfileType | None:
    return get_repo("corporation_profile").resolve_single(info, **kwargs)


@method_cache(
    ttl=Config.get_cache_ttl(),
    cache_name=Config.get_cache_name("queries", "corporation_profile"),
    cache_enabled=Config.is_cache_enabled,
)
def resolve_corporation_profile_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CorporationProfileListType:
    return get_repo("corporation_profile").list(info, **kwargs)
