#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import traceback
from typing import Any, Dict

from graphene import Boolean, Field, Int, Mutation, String
from silvaengine_utility import JSONCamelCase

from ..models.repositories import get_repo
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
            activity_history = get_repo("activity_history").insert(info, **kwargs)
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
            ok = get_repo("activity_history").delete(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteActivityHistory(ok=ok)
