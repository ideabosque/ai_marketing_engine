#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import traceback
from typing import Any, Dict

from graphene import Boolean, Field, Int, List, Mutation, String

from silvaengine_utility import JSON

from ..models.question import delete_question, insert_update_question
from ..types.question import QuestionType


class InsertUpdateQuestion(Mutation):
    question = Field(QuestionType)

    class Arguments:
        question_uuid = String(required=False)
        question_group_uuid = String(required=False)
        wizard_uuid = String(required=False)
        data_type = String(required=False)
        question = String(required=False)
        priority = Int(required=False)
        attribute_name = String(required=False)
        attribute_type = String(required=False)
        option_values = List(String, required=False)
        condition = List(JSON, required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateQuestion":
        try:
            question = insert_update_question(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateQuestion(question=question)


class DeleteQuestion(Mutation):
    ok = Boolean()

    class Arguments:
        question_uuid = String(required=True)

    @staticmethod
    def mutate(root: Any, info: Any, **kwargs: Dict[str, Any]) -> "DeleteQuestion":
        try:
            ok = delete_question(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteQuestion(ok=ok)
