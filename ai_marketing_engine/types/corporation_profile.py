#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON

from ..models.utils import _get_data


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
        endpoint_id = getattr(parent, "endpoint_id", None)
        corporation_uuid = getattr(parent, "corporation_uuid", None)
        if not endpoint_id or not corporation_uuid:
            return None

        return _get_data(endpoint_id, corporation_uuid, "corporation")


class CorporationProfileListType(ListObjectType):
    corporation_profile_list = List(CorporationProfileType)
