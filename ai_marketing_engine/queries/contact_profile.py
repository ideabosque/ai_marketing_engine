#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from silvaengine_utility import method_cache

from ..handlers.config import Config

from ..models import contact_profile
from ..types.contact_profile import ContactProfileListType, ContactProfileType


def resolve_contact_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactProfileType | None:
    return contact_profile.resolve_contact_profile(info, **kwargs)


@method_cache(
    ttl=Config.get_cache_ttl(),
    cache_name=Config.get_cache_name("queries", "contact_profile"),
    cache_enabled=Config.is_cache_enabled,
)
def resolve_contact_profile_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactProfileListType:
    return contact_profile.resolve_contact_profile_list(info, **kwargs)
