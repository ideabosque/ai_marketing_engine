#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from silvaengine_utility import method_cache

from ..handlers.config import Config

from ..models import corporation_profile
from ..types.corporation_profile import (
    CorporationProfileListType,
    CorporationProfileType,
)


def resolve_corporation_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CorporationProfileType | None:
    return corporation_profile.resolve_corporation_profile(info, **kwargs)


@method_cache(ttl=Config.get_cache_ttl(), cache_name=Config.get_cache_name('queries', 'corporation_profile'))
def resolve_corporation_profile_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CorporationProfileListType:
    return corporation_profile.resolve_corporation_profile_list(info, **kwargs)
