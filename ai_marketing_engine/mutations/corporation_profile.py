#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import traceback
from typing import Any, Dict

from graphene import Boolean, Field, List, Mutation, String

from silvaengine_utility import JSON

from ..models.corporation_profile import (
    delete_corporation_profile,
    insert_update_corporation_profile,
)
from ..types.corporation_profile import CorporationProfileType


class InsertUpdateCorporationProfile(Mutation):
    corporation_profile = Field(CorporationProfileType)

    class Arguments:
        corporation_uuid = String(required=False)
        external_id = String(required=False)
        corporation_type = String(required=False)
        business_name = String(required=False)
        categories = List(String, required=False)
        address = JSON(required=False)
        data = JSON(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateCorporationProfile":
        try:
            corporation_profile = insert_update_corporation_profile(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateCorporationProfile(corporation_profile=corporation_profile)


class DeleteCorporationProfile(Mutation):
    ok = Boolean()

    class Arguments:
        corporation_uuid = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteCorporationProfile":
        try:
            ok = delete_corporation_profile(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteCorporationProfile(ok=ok)
