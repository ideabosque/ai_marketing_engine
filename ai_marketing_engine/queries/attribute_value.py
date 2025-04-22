#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from ..models import attribute_value
from ..types.attribute_value import AttributeValueListType, AttributeValueType


def resolve_attribute_value(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> AttributeValueType:
    return attribute_value.resolve_attribute_value(info, **kwargs)


def resolve_attribute_value_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> AttributeValueListType:
    return attribute_value.resolve_attribute_value_list(info, **kwargs)
