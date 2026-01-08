#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo
from silvaengine_utility import method_cache

from ..handlers import ai_marketing_utility
from ..handlers.config import Config
from ..types.ai_marketing import CrmUserListType, PresignedUploadUrlType


def resolve_presigned_upload_url(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> PresignedUploadUrlType:
    return ai_marketing_utility.resolve_presigned_upload_url(info, **kwargs)


@method_cache(
    ttl=Config.get_cache_ttl(),
    cache_name=Config.get_cache_name("queries", "ai_marketing"),
)
def resolve_crm_user_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CrmUserListType:
    return ai_marketing_utility.resolve_crm_user_list(info, **kwargs)
