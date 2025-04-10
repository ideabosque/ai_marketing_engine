#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from ..models import utm_tag_data_collection
from ..types.utm_tag_data_collection import (
    UtmTagDataCollectionListType,
    UtmTagDataCollectionType,
)


def resolve_utm_tag_data_collection(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> UtmTagDataCollectionType:
    return utm_tag_data_collection.resolve_utm_tag_data_collection(info, **kwargs)


def resolve_utm_tag_data_collection_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> UtmTagDataCollectionListType:
    return utm_tag_data_collection.resolve_utm_tag_data_collection_list(info, **kwargs)
