#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, Decimal, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON


class ActivityHistoryType(ObjectType):
    id = String()
    timestamp = Decimal()
    log = String()
    data_diff = JSON()
    type = String()
    updated_by = String()
    updated_at = DateTime()


class ActivityHistoryListType(ListObjectType):
    activity_history_list = List(ActivityHistoryType)
