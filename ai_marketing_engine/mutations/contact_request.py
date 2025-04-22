#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import traceback
from typing import Any, Dict

from graphene import Boolean, Field, Mutation, String

from ..models.contact_request import (
    delete_contact_request,
    insert_update_contact_request,
)
from ..types.contact_request import ContactRequestType


class InsertUpdateContactRequest(Mutation):
    contact_request = Field(ContactRequestType)

    class Arguments:
        contact_uuid = String(required=False)
        request_uuid = String(required=False)
        place_uuid = String(required=False)
        request_title = String(required=False)
        request_detail = String(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateContactRequest":
        try:
            contact_request = insert_update_contact_request(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateContactRequest(contact_request=contact_request)


class DeleteContactRequest(Mutation):
    ok = Boolean()

    class Arguments:
        request_uuid = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteContactRequest":
        try:
            ok = delete_contact_request(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteContactRequest(ok=ok)
