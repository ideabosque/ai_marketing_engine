#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, Decimal, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON


class AttributeValueType(ObjectType):
    data_type = String()
    value_version_uuid = String()
    attribute_name = String()
    data_identity = String()
    endpoint_id = String()
    value = String()
    status = String()
    updated_by = String()
    updated_at = DateTime()
    created_by = String()


class AttributeValueListType(ListObjectType):
    attribute_value_list = List(AttributeValueType)
