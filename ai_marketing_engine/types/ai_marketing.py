#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import Int, ObjectType, String


class PresignedUploadUrlType(ObjectType):
    url = String()
    object_key = String()
    expiration = Int()
