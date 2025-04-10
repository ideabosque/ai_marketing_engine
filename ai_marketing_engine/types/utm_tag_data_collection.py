#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON


class UtmTagDataCollectionType(ObjectType):
    endpoint_id = String()
    collection_uuid = String()
    tag_name = String()
    contact_profile = JSON()
    keyword = String()
    utm_campaign = String()
    utm_content = String()
    utm_medium = String()
    utm_source = String()
    utm_term = String()
    created_at = DateTime()


class UtmTagDataCollectionListType(ListObjectType):
    utm_tag_data_collection_list = List(UtmTagDataCollectionType)
