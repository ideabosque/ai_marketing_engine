#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import traceback
from typing import Any, Dict

from graphene import Boolean, Field, List, Mutation, String

from ..models.place import delete_place, insert_update_place
from ..types.place import PlaceType


class InsertUpdatePlace(Mutation):
    place = Field(PlaceType)

    class Arguments:
        place_uuid = String(required=False)
        region = String(required=False)
        latitude = String(required=False)
        longitude = String(required=False)
        business_name = String(required=False)
        address = String(required=False)
        phone_number = String(required=False)
        website = String(required=False)
        types = List(String, required=False)
        corporation_uuid = String(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(root: Any, info: Any, **kwargs: Dict[str, Any]) -> "InsertUpdatePlace":
        try:
            place = insert_update_place(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdatePlace(place=place)


class DeletePlace(Mutation):
    ok = Boolean()

    class Arguments:
        place_uuid = String(required=True)

    @staticmethod
    def mutate(root: Any, info: Any, **kwargs: Dict[str, Any]) -> "DeletePlace":
        try:
            ok = delete_place(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeletePlace(ok=ok)
