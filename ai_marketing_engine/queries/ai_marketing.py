#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from ..handlers import ai_marketing_utility
from ..types.ai_marketing import PresignedUploadUrlType


def resolve_presigned_upload_url(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> PresignedUploadUrlType:
    return ai_marketing_utility.resolve_presigned_upload_url(info, **kwargs)
