#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import traceback
from typing import Any, Dict

from graphene import Boolean, Field, Mutation, String

from silvaengine_utility import JSON

from ..models.contact_profile import (
    delete_contact_profile,
    insert_update_contact_profile,
)
from ..types.contact_profile import ContactProfileType


class InsertUpdateContactProfile(Mutation):
    contact_profile = Field(ContactProfileType)

    class Arguments:
        place_uuid = String(required=True)
        contact_uuid = String(required=False)
        email = String(required=False)
        endpoint_id = String(required=False)
        first_name = String(required=False)
        last_name = String(required=False)
        data = JSON(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateContactProfile":
        try:
            contact_profile = insert_update_contact_profile(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateContactProfile(contact_profile=contact_profile)


class DeleteContactProfile(Mutation):
    ok = Boolean()

    class Arguments:
        place_uuid = String(required=True)
        contact_uuid = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteContactProfile":
        try:
            ok = delete_contact_profile(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteContactProfile(ok=ok)
