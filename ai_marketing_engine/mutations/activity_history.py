#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import traceback
from typing import Any, Dict

from graphene import Boolean, Field, Int, Mutation, String

from silvaengine_utility import JSONCamelCase

from ..models.activity_history import delete_activity_history, insert_activity_history
from ..types.activity_history import ActivityHistoryType


class InsertActivityHistory(Mutation):
    activity_history = Field(ActivityHistoryType)

    class Arguments:
        id = String(required=True)
        data_diff = JSONCamelCase(required=False)
        log = String(required=False)
        type = String(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertActivityHistory":
        try:
            activity_history = insert_activity_history(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertActivityHistory(activity_history=activity_history)


class DeleteActivityHistory(Mutation):
    ok = Boolean()

    class Arguments:
        id = String(required=True)
        timestamp = Int(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteActivityHistory":
        try:
            ok = delete_activity_history(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteActivityHistory(ok=ok)
