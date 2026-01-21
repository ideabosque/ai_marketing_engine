#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, Decimal, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSONCamelCase

class AttributeValueType(ObjectType):
    data_type_attribute_name = String()
    value_version_uuid = String()
    data_identity = String()
    partition_key = String()
    value = String()
    status = String()
    updated_by = String()
    updated_at = DateTime()
    created_at = DateTime()


class AttributeValueListType(ListObjectType):
    attribute_value_list = List(AttributeValueType)
