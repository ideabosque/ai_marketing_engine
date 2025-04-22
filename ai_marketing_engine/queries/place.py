#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from ..models import place
from ..types.place import PlaceListType, PlaceType


def resolve_place(info: ResolveInfo, **kwargs: Dict[str, Any]) -> PlaceType:
    return place.resolve_place(info, **kwargs)


def resolve_place_list(info: ResolveInfo, **kwargs: Dict[str, Any]) -> PlaceListType:
    return place.resolve_place_list(info, **kwargs)
