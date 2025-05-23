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
from tenacity import retry, stop_after_attempt, wait_exponential

from silvaengine_dynamodb_base import (
    BaseModel,
    delete_decorator,
    insert_update_decorator,
    monitor_decorator,
    resolve_list_decorator,
)
from silvaengine_utility import Utility

from ..types.wizard import WizardListType, WizardType
from .utils import _get_questions


class WizardModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-wizards"

    endpoint_id = UnicodeAttribute(hash_key=True)
    wizard_uuid = UnicodeAttribute(range_key=True)
    wizard_title = UnicodeAttribute()
    wizard_description = UnicodeAttribute(null=True)
    wizard_type = UnicodeAttribute()
    form_schema = UnicodeAttribute(null=True)
    embed_content = UnicodeAttribute(null=True)
    priority = NumberAttribute(default=0)
    question_uuids = ListAttribute(of=UnicodeAttribute, null=True)
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()


def create_wizard_table(logger: logging.Logger) -> bool:
    """Create the Wizard table if it doesn't exist."""
    if not WizardModel.exists():
        # Create with on-demand billing (PAY_PER_REQUEST)
        WizardModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        logger.info("The Wizard table has been created.")
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_wizard(endpoint_id: str, wizard_uuid: str) -> WizardModel:
    return WizardModel.get(endpoint_id, wizard_uuid)


def get_wizard_count(endpoint_id: str, wizard_uuid: str) -> int:
    return WizardModel.count(endpoint_id, WizardModel.wizard_uuid == wizard_uuid)


def get_wizard_type(info: ResolveInfo, wizard: WizardModel) -> WizardType:
    try:
        questions = _get_questions(info.context["endpoint_id"], wizard.question_uuids)
        wizard = wizard.__dict__["attribute_values"]
        wizard["questions"] = questions
        wizard.pop("question_uuids")
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    return WizardType(**Utility.json_loads(Utility.json_dumps(wizard)))


def resolve_wizard(info: ResolveInfo, **kwargs: Dict[str, Any]) -> WizardType:
    count = get_wizard_count(info.context["endpoint_id"], kwargs.get("wizard_uuid"))
    if count == 0:
        return None

    return get_wizard_type(
        info,
        get_wizard(info.context["endpoint_id"], kwargs.get("wizard_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "wizard_uuid"],
    list_type_class=WizardListType,
    type_funct=get_wizard_type,
)
def resolve_wizard_list(info: ResolveInfo, **kwargs: Dict[str, Any]) -> Any:
    endpoint_id = info.context["endpoint_id"]
    wizard_title = kwargs.get("wizard_title")
    wizard_description = kwargs.get("wizard_description")
    priority = kwargs.get("priority")
    wizard_types = kwargs.get("wizard_types")

    args = []
    inquiry_funct = WizardModel.scan
    count_funct = WizardModel.count
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = WizardModel.query

    the_filters = None  # We can add filters for the query.
    if wizard_title:
        the_filters &= WizardModel.wizard_title.contains(wizard_title)
    if wizard_description:
        the_filters &= WizardModel.wizard_description.contains(wizard_description)
    if priority:
        the_filters &= WizardModel.priority == priority
    if wizard_types:
        the_filters &= WizardModel.wizard_type.is_in(*wizard_types)

    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "wizard_uuid",
    },
    model_funct=get_wizard,
    count_funct=get_wizard_count,
    type_funct=get_wizard_type,
)
def insert_update_wizard(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    wizard_uuid = kwargs.get("wizard_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "wizard_title": kwargs["wizard_title"],
            "wizard_type": kwargs["wizard_type"],
            "question_uuids": [],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        for key in [
            "wizard_description",
            "form_schema",
            "embed_content",
            "priority",
            "question_uuids",
        ]:
            if key in kwargs:
                cols[key] = kwargs[key]
        WizardModel(endpoint_id, wizard_uuid, **cols).save()
        return

    wizard = kwargs.get("entity")
    actions = [
        WizardModel.updated_by.set(kwargs["updated_by"]),
        WizardModel.updated_at.set(pendulum.now("UTC")),
    ]

    # Map of kwargs keys to WizardModel attributes
    field_map = {
        "wizard_title": WizardModel.wizard_title,
        "wizard_description": WizardModel.wizard_description,
        "wizard_type": WizardModel.wizard_type,
        "form_schema": WizardModel.form_schema,
        "embed_content": WizardModel.embed_content,
        "priority": WizardModel.priority,
        "question_uuids": WizardModel.question_uuids,
    }

    # Add actions dynamically based on the presence of keys in kwargs
    for key, field in field_map.items():
        if key in kwargs:  # Check if the key exists in kwargs
            actions.append(field.set(None if kwargs[key] == "null" else kwargs[key]))

    # Update the wizard
    wizard.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "wizard_uuid",
    },
    model_funct=get_wizard,
)
def delete_wizard(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True
