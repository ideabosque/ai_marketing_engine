#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import traceback
from typing import Any, Dict

from graphene import Boolean, Field, Int, Mutation, String

from silvaengine_utility import JSON

from ..models.question_group import delete_question_group, insert_update_question_group
from ..types.question_group import QuestionGroupType


class InsertUpdateQuestionGroup(Mutation):
    question_group = Field(QuestionGroupType)

    class Arguments:
        question_group_uuid = String(required=False)
        question_group_name = String(required=False)
        question_group_description = String(required=False)
        region = String(required=False)
        question_criteria = JSON(required=False)
        weight = Int(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateQuestionGroup":
        try:
            question_group = insert_update_question_group(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateQuestionGroup(question_group=question_group)


class DeleteQuestionGroup(Mutation):
    ok = Boolean()

    class Arguments:
        question_group_uuid = String(required=True)

    @staticmethod
    def mutate(root: Any, info: Any, **kwargs: Dict[str, Any]) -> "DeleteQuestionGroup":
        try:
            ok = delete_question_group(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteQuestionGroup(ok=ok)
