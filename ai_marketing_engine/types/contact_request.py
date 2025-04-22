#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON


class ContactRequestType(ObjectType):
    contact_profile = JSON()
    endpoint_id = String()
    request_uuid = String()
    request_title = String()
    request_detail = String()
    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()


class ContactRequestListType(ListObjectType):
    contact_request_list = List(ContactRequestType)
