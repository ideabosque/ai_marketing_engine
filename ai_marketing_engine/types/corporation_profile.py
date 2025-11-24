#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON

from ..models.batch_loaders import get_loaders


class CorporationProfileType(ObjectType):
    endpoint_id = String()
    corporation_uuid = String()
    external_id = String()
    corporation_type = String()
    business_name = String()
    categories = List(String)
    address = String()

    # Dynamic attributes bag – still JSON, but lazily resolved
    data = JSON()

    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()

    # ------- Nested / dynamic resolvers -------

    def resolve_data(parent, info):
        """
        Resolve dynamic attributes for corporation profiles on demand.
        Uses AttributeValueModel via _get_data(..., "corporation").
        """
        existing_data = getattr(parent, "data", None)
        if isinstance(existing_data, dict):
            return existing_data

        endpoint_id = getattr(parent, "endpoint_id", None)
        corporation_uuid = getattr(parent, "corporation_uuid", None)
        if not endpoint_id or not corporation_uuid:
            return None

        loaders = get_loaders(info.context)
        return loaders.corporation_data_loader.load((endpoint_id, corporation_uuid))


class CorporationProfileListType(ListObjectType):
    corporation_profile_list = List(CorporationProfileType)
