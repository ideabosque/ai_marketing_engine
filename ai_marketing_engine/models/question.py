#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
import traceback
from typing import Any, Dict

import pendulum
from graphene import ResolveInfo
from pynamodb.attributes import (
    ListAttribute,
    MapAttribute,
    NumberAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.indexes import AllProjection, LocalSecondaryIndex
from tenacity import retry, stop_after_attempt, wait_exponential

from silvaengine_dynamodb_base import (
    BaseModel,
    delete_decorator,
    insert_update_decorator,
    monitor_decorator,
    resolve_list_decorator,
)
from silvaengine_utility import Utility

from ..types.question import QuestionListType, QuestionType
from .utils import _get_wizard


class DataTypeIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "data_type-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    endpoint_id = UnicodeAttribute(hash_key=True)
    data_type = UnicodeAttribute(range_key=True)


class WizardUuidIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "wizard_uuid-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    endpoint_id = UnicodeAttribute(hash_key=True)
    wizard_uuid = UnicodeAttribute(range_key=True)


class QuestionGroupUuidIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "question_group_uuid-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    endpoint_id = UnicodeAttribute(hash_key=True)
    question_group_uuid = UnicodeAttribute(range_key=True)


class QuestionModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-questions"

    endpoint_id = UnicodeAttribute(hash_key=True)
    question_uuid = UnicodeAttribute(range_key=True)
    question_group_uuid = UnicodeAttribute()
    wizard_uuid = UnicodeAttribute()
    data_type = UnicodeAttribute()
    question = UnicodeAttribute(null=True)
    priority = NumberAttribute()
    attribute_name = UnicodeAttribute()
    attribute_type = UnicodeAttribute(default="string")
    option_values = ListAttribute(of=UnicodeAttribute, null=True)
    condition = ListAttribute(of=MapAttribute, null=True)
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    question_group_uuid_index = QuestionGroupUuidIndex()
    wizard_uuid_index = WizardUuidIndex()
    data_type_index = DataTypeIndex()


def create_question_table(logger: logging.Logger) -> bool:
    """Create the Question table if it doesn't exist."""
    if not QuestionModel.exists():
        # Create with on-demand billing (PAY_PER_REQUEST)
        QuestionModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        logger.info("The Question table has been created.")
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_question(endpoint_id: str, question_uuid: str) -> QuestionModel:
    return QuestionModel.get(endpoint_id, question_uuid)


def get_question_count(endpoint_id: str, question_uuid: str) -> int:
    return QuestionModel.count(
        endpoint_id, QuestionModel.question_uuid == question_uuid
    )


def get_question_type(info: ResolveInfo, question: QuestionModel) -> QuestionType:
    try:
        wizard = _get_wizard(question.endpoint_id, question.wizard_uuid)
        question = question.__dict__["attribute_values"]
        question["priority"] = (
            wizard["question_group"]["weight"] * 10 + question["priority"]
        )
        question["wizard"] = wizard
        question.pop("wizard_uuid")
        question.pop("question_group_uuid")
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e

    return QuestionType(**Utility.json_loads(Utility.json_dumps(question)))


def resolve_question(info: ResolveInfo, **kwargs: Dict[str, Any]) -> QuestionType:
    return get_question_type(
        info,
        get_question(info.context["endpoint_id"], kwargs.get("question_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "question_uuid", "wizard_uuid", "data_type"],
    list_type_class=QuestionListType,
    type_funct=get_question_type,
)
def resolve_question_list(info: ResolveInfo, **kwargs: Dict[str, Any]) -> Any:
    endpoint_id = info.context["endpoint_id"]
    wizard_uuid = kwargs.get("wizard_uuid")
    data_type = kwargs.get("data_type")
    question_group_uuid = kwargs.get("question_group_uuid")
    question = kwargs.get("question")
    attribute_name = kwargs.get("attribute_name")
    attribute_type = kwargs.get("attribute_type")

    args = []
    inquiry_funct = QuestionModel.scan
    count_funct = QuestionModel.count
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = QuestionModel.query
        if wizard_uuid:
            count_funct = QuestionModel.wizard_uuid_index.count
            args[1] = QuestionModel.wizard_uuid_index == wizard_uuid
            inquiry_funct = QuestionModel.wizard_uuid_index.query
        if data_type:
            count_funct = QuestionModel.data_type_index.count
            args[1] = QuestionModel.data_type_index == data_type
            inquiry_funct = QuestionModel.data_type_index.query

    the_filters = None  # We can add filters for the query.
    if question_group_uuid:
        the_filters &= QuestionModel.question_group_uuid == question_group_uuid
    if question:
        the_filters &= QuestionModel.question.contains(question)
    if attribute_name:
        the_filters &= QuestionModel.attribute_name == attribute_name
    if attribute_type:
        the_filters &= QuestionModel.attribute_type == attribute_type
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "question_uuid",
    },
    model_funct=get_question,
    count_funct=get_question_count,
    type_funct=get_question_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_question(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    question_uuid = kwargs.get("question_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "question_group_uuid": kwargs["question_group_uuid"],
            "wizard_uuid": kwargs["wizard_uuid"],
            "data_type": kwargs["data_type"],
            "priority": kwargs["priority"],
            "attribute_name": kwargs["attribute_name"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        for key in ["question", "option_values", "condition", "attribute_type"]:
            if key in kwargs:
                cols[key] = kwargs[key]
        QuestionModel(
            endpoint_id,
            question_uuid,
            **cols,
        ).save()
        return

    question = kwargs.get("entity")
    actions = [
        QuestionModel.updated_by.set(kwargs["updated_by"]),
        QuestionModel.updated_at.set(pendulum.now("UTC")),
    ]

    # Map of kwargs keys to QuestionModel attributes
    field_map = {
        "question_group_uuid": QuestionModel.question_group_uuid,
        "wizard_uuid": QuestionModel.wizard_uuid,
        "data_type": QuestionModel.data_type,
        "question": QuestionModel.question,
        "priority": QuestionModel.priority,
        "attribute_name": QuestionModel.attribute_name,
        "attribute_type": QuestionModel.attribute_type,
        "option_values": QuestionModel.option_values,
        "condition": QuestionModel.condition,
    }

    # Add actions dynamically based on the presence of keys in kwargs
    for key, field in field_map.items():
        if key in kwargs:  # Check if the key exists in kwargs
            actions.append(field.set(None if kwargs[key] == "null" else kwargs[key]))

    # Update the question
    question.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "question_uuid",
    },
    model_funct=get_question,
)
def delete_question(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True
