#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, Field, List, ObjectType, String
from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON

from ..models.batch_loaders import get_loaders


class CorporationProfileType(ObjectType):
    partition_key = String()
    corporation_uuid = String()
    external_id = String()
    endpoint_id = String()
    part_id = String()
    corporation_type = String()
    business_name = String()
    categories = List(String)
    address = String()

    # Dynamic attributes bag – still JSON, but lazily resolved
    data = Field(JSON)

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

        partition_key = getattr(parent, "partition_key", None)
        corporation_uuid = getattr(parent, "corporation_uuid", None)
        if not partition_key or not corporation_uuid:
            return None
        loaders = get_loaders(info.context)
        return loaders.corporation_data_loader.load((partition_key, corporation_uuid))


class CorporationProfileListType(ListObjectType):
    corporation_profile_list = List(CorporationProfileType)
