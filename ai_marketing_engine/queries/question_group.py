#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from ..models import question_group
from ..types.question_group import QuestionGroupListType, QuestionGroupType


def resolve_question_group(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> QuestionGroupType:
    return question_group.resolve_question_group(info, **kwargs)


def resolve_question_group_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> QuestionGroupListType:
    return question_group.resolve_question_group_list(info, **kwargs)
