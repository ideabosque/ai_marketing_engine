#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON


class CorporationProfileType(ObjectType):
    endpoint_id = String()
    corporation_uuid = String()
    external_id = String()
    corporation_type = String()
    business_name = String()
    categories = List(String)
    address = String()
    data = JSON()
    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()


class CorporationProfileListType(ListObjectType):
    corporation_profile_list = List(CorporationProfileType)
