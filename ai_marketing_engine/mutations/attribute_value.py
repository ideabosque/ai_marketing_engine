#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import traceback
from typing import Any, Dict

from graphene import Boolean, Field, Mutation, String

from ..models.attribute_value import (
    delete_attribute_value,
    insert_update_attribute_value,
)
from ..types.attribute_value import AttributeValueType


class InsertUpdateAttributeValue(Mutation):
    attribute_value = Field(AttributeValueType)

    class Arguments:
        data_type_attribute_name = String(required=True)
        value_version_uuid = String(required=False)
        data_identity = String(required=True)
        value = String(required=False)
        status = String(required=False)
        value = String(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateAttributeValue":
        try:
            attribute_value = insert_update_attribute_value(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateAttributeValue(attribute_value=attribute_value)


class DeleteAttributeValue(Mutation):
    ok = Boolean()

    class Arguments:
        data_type_attribute_name = String(required=True)
        value_version_uuid = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteAttributeValue":
        try:
            ok = delete_attribute_value(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteAttributeValue(ok=ok)
