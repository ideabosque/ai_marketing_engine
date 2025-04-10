#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON


class PlaceType(ObjectType):
    endpoint_id = String()
    place_uuid = String()
    region = String()
    latitude = String()
    longitude = String()
    business_name = String()
    address = String()
    phone_number = String()
    website = String()
    types = List(String)
    corporation_profile = JSON()
    updated_by = String()
    updated_at = DateTime()
    created_at = DateTime()


class PlaceListType(ListObjectType):
    place_list = List(PlaceType)
