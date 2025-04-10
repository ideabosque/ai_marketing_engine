#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, Int, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON


class QuestionType(ObjectType):
    endpoint_id = String()
    question_uuid = String()
    question_group_uuid = String()
    wizard_uuid = String()
    data_type = String()
    question = String()
    priority = Int()
    attribute_name = String()
    attribute_type = String()
    option_values = List(String)
    condition = List(JSON)
    updated_by = String()
    updated_at = DateTime()
    created_at = DateTime()


class QuestionListType(ListObjectType):
    question_list = List(QuestionType)
