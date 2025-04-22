#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from ..models import activity_history
from ..types.activity_history import ActivityHistoryListType, ActivityHistoryType


def resolve_activity_history(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ActivityHistoryType:
    return activity_history.resolve_activity_history(info, **kwargs)


def resolve_activity_history_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ActivityHistoryListType:
    return activity_history.resolve_activity_history_list(info, **kwargs)
