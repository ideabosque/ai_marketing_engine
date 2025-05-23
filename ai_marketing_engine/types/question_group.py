#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, Int, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON


class QuestionGroupType(ObjectType):
    endpoint_id = String()
    question_group_uuid = String()
    question_group_name = String()
    question_group_description = String()
    region = String()
    question_criteria = JSON()
    weight = Int()
    wizards = List(JSON)
    updated_by = String()
    updated_at = DateTime()
    created_at = DateTime()


class QuestionGroupListType(ListObjectType):
    question_group_list = List(QuestionGroupType)
