#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from ..models import contact_request
from ..types.contact_request import ContactRequestListType, ContactRequestType


def resolve_contact_request(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactRequestType:
    return contact_request.resolve_contact_request(info, **kwargs)


def resolve_contact_request_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactRequestListType:
    return contact_request.resolve_contact_request_list(info, **kwargs)
