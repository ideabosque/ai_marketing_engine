#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo
from silvaengine_utility import method_cache

from ..handlers.config import Config
from ..models import activity_history
from ..types.activity_history import ActivityHistoryListType, ActivityHistoryType


def resolve_activity_history(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ActivityHistoryType:
    return activity_history.resolve_activity_history(info, **kwargs)


@method_cache(
    ttl=Config.get_cache_ttl(),
    cache_name=Config.get_cache_name("queries", "activity_history"),
)
def resolve_activity_history_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ActivityHistoryListType:
    return activity_history.resolve_activity_history_list(info, **kwargs)
