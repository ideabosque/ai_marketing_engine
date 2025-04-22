#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON


class ContactProfileType(ObjectType):
    endpoint_id = String()
    place = JSON()
    contact_uuid = String()
    email = String()
    first_name = String()
    last_name = String()
    data = JSON()
    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()


class ContactProfileListType(ListObjectType):
    contact_profile_list = List(ContactProfileType)
