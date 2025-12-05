#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
import traceback
from typing import Any, Dict, List

import pendulum
from graphene import ResolveInfo
from pynamodb.attributes import (
    ListAttribute,
    MapAttribute,
    NumberAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
)
from tenacity import retry, stop_after_attempt, wait_exponential

from silvaengine_dynamodb_base import (
    BaseModel,
    delete_decorator,
    insert_update_decorator,
    monitor_decorator,
    resolve_list_decorator,
)
from silvaengine_utility import Utility

from ..types.question_group import QuestionGroupListType, QuestionGroupType
from .corporation_profile import get_corporation_profile
from .place import get_place
from .utils import _get_wizards


class QuestionGroupModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-question_groups"

    endpoint_id = UnicodeAttribute(hash_key=True)
    question_group_uuid = UnicodeAttribute(range_key=True)
    question_group_name = UnicodeAttribute()
    question_group_description = UnicodeAttribute(null=True)
    region = UnicodeAttribute()
    question_criteria = MapAttribute()
    weight = NumberAttribute(default=0)
    wizard_uuids = ListAttribute(of=UnicodeAttribute, null=True)
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()


def create_question_group_table(logger: logging.Logger) -> bool:
    """Create the QuestionGroup table if it doesn't exist."""
    if not QuestionGroupModel.exists():
        # Create with on-demand billing (PAY_PER_REQUEST)
        QuestionGroupModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        logger.info("The QuestionGroup table has been created.")
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_question_group(
    endpoint_id: str, question_group_uuid: str
) -> QuestionGroupModel:
    return QuestionGroupModel.get(endpoint_id, question_group_uuid)


def get_question_group_count(endpoint_id: str, question_group_uuid: str) -> int:
    return QuestionGroupModel.count(
        endpoint_id, QuestionGroupModel.question_group_uuid == question_group_uuid
    )


def get_question_group_type(
    info: ResolveInfo, question_group: QuestionGroupModel
) -> QuestionGroupType:
    try:
        if not question_group.wizard_uuids:
            question_group.wizard_uuids = []
        wizards = _get_wizards(question_group.endpoint_id, question_group.wizard_uuids)
        question_group = question_group.__dict__["attribute_values"]
        question_group["wizards"] = wizards
        question_group.pop("wizard_uuids")
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    return QuestionGroupType(**Utility.json_normalize(question_group))


def resolve_question_group(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> QuestionGroupType:
    count = get_question_group_count(
        info.context["endpoint_id"], kwargs.get("question_group_uuid")
    )
    if count == 0:
        return None

    return get_question_group_type(
        info,
        get_question_group(
            info.context["endpoint_id"], kwargs.get("question_group_uuid")
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "question_group_uuid"],
    list_type_class=QuestionGroupListType,
    type_funct=get_question_group_type,
)
def resolve_question_group_list(info: ResolveInfo, **kwargs: Dict[str, Any]) -> Any:
    endpoint_id = info.context["endpoint_id"]
    question_name = kwargs.get("question_name")
    question_description = kwargs.get("question_description")
    region = kwargs.get("region")
    question_criteria = kwargs.get("question_criteria")

    if kwargs.get("place_uuid"):
        place = get_place(endpoint_id, kwargs.get("place_uuid"))
        # corporation_profile = get_corporation_profile(
        #     endpoint_id, place.corporation_uuid
        # )
        region = place.region
        # question_criteria = {
        #     "place_types": place.types,
        #     "corporation_uuid": place.corporation_uuid,
        # }
        # if corporation_profile:
        #     question_criteria.update(
        #         {
        #             "corporation_type": corporation_profile.corporation_type,
        #             "corporation_categories": corporation_profile.categories,
        #         }
        #     )
        # if kwargs.get("utm_tag_name"):
        #     question_criteria.update({"utm_tag_name": kwargs["utm_tag_name"]})

    args = []
    inquiry_funct = QuestionGroupModel.scan
    count_funct = QuestionGroupModel.count
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = QuestionGroupModel.query

    the_filters = None  # We can add filters for the query.
    if question_name:
        the_filters &= QuestionGroupModel.question_group_name.contains(question_name)
    if question_description:
        the_filters &= QuestionGroupModel.question_group_description.contains(
            question_description
        )
    if region:
        the_filters &= QuestionGroupModel.region == region
    if question_criteria:
        if question_criteria.get("place_types"):
            the_filters &= QuestionGroupModel.question_criteria["place_type"].exists()
            the_filters &= QuestionGroupModel.question_criteria["place_type"].is_in(
                *question_criteria["place_types"]
            )
        if question_criteria.get("corporation_type"):
            the_filters &= QuestionGroupModel.question_criteria[
                "corporation_type"
            ].exists()
            the_filters &= (
                QuestionGroupModel.question_criteria["corporation_type"]
                == question_criteria["corporation_type"]
            )
        if question_criteria.get("corporation_categories"):
            the_filters &= QuestionGroupModel.question_criteria[
                "corporation_category"
            ].exists()
            the_filters &= QuestionGroupModel.question_criteria[
                "corporation_category"
            ].is_in(*question_criteria["corporation_categories"])
        if question_criteria.get("utm_tag_name"):
            the_filters &= QuestionGroupModel.question_criteria["utm_tag_name"].exists()
            the_filters &= (
                QuestionGroupModel.question_criteria["utm_tag_name"]
                == question_criteria["utm_tag_name"]
            )
        if question_criteria.get("corporation_uuid"):
            the_filters &= QuestionGroupModel.question_criteria[
                "corporation_uuids"
            ].exists()
            the_filters &= QuestionGroupModel.question_criteria[
                "corporation_uuids"
            ].contains(question_criteria["corporation_uuid"])
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "question_group_uuid",
    },
    model_funct=get_question_group,
    count_funct=get_question_group_count,
    type_funct=get_question_group_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_question_group(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    question_group_uuid = kwargs.get("question_group_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "question_criteria": {},
            "wizard_uuid": [],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        for key in [
            "question_criteria",
            "question_group_name",
            "question_group_description",
            "region",
            "weight",
            "wizard_uuid",
        ]:
            if key in kwargs:
                cols[key] = kwargs[key]
        QuestionGroupModel(endpoint_id, question_group_uuid, **cols).save()
        return

    question_group = kwargs.get("entity")
    actions = [
        QuestionGroupModel.updated_by.set(kwargs["updated_by"]),
        QuestionGroupModel.updated_at.set(pendulum.now("UTC")),
    ]

    # Map of kwargs keys to QuestionGroupModel attributes
    field_map = {
        "question_group_name": QuestionGroupModel.question_group_name,
        "question_group_description": QuestionGroupModel.question_group_description,
        "region": QuestionGroupModel.region,
        "question_criteria": QuestionGroupModel.question_criteria,
        "weight": QuestionGroupModel.weight,
        "wizard_uuid": QuestionGroupModel.wizard_uuids,
    }

    # Add actions dynamically based on the presence of keys in kwargs
    for key, field in field_map.items():
        if key in kwargs:  # Check if the key exists in kwargs
            actions.append(field.set(None if kwargs[key] == "null" else kwargs[key]))

    # Update the question criteria
    question_group.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "question_group_uuid",
    },
    model_funct=get_question_group,
)
def delete_question_group(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True
