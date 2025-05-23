#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from ..models import contact_profile
from ..types.contact_profile import ContactProfileListType, ContactProfileType


def resolve_contact_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactProfileType:
    return contact_profile.resolve_contact_profile(info, **kwargs)


def resolve_contact_profile_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactProfileListType:
    return contact_profile.resolve_contact_profile_list(info, **kwargs)
