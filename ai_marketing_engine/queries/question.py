#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from ..models import question
from ..types.question import QuestionListType, QuestionType


def resolve_question(info: ResolveInfo, **kwargs: Dict[str, Any]) -> QuestionType:
    return question.resolve_question(info, **kwargs)


def resolve_question_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> QuestionListType:
    return question.resolve_question_list(info, **kwargs)
