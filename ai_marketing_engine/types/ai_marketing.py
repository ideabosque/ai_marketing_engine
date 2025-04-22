#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import Int, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType


class PresignedUploadUrlType(ObjectType):
    url = String()
    object_key = String()
    expiration = Int()


class CrmUserType(ObjectType):
    email = String()
    first_name = String()
    last_name = String()


class CrmUserListType(ListObjectType):
    crm_user_list = List(CrmUserType)
