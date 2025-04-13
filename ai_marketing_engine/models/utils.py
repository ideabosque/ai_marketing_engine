# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
from typing import Any, Dict, List


def _initialize_tables(logger: logging.Logger) -> None:
    from .activity_history import create_activity_history_table
    from .attribute_value import create_attribute_value_table
    from .contact_profile import create_contact_profile_table
    from .contact_request import create_contact_request_table
    from .corporation_profile import create_corporation_profile_table
    from .place import create_place_table
    from .question import create_question_table
    from .question_group import create_question_group_table
    from .utm_tag_data_collection import create_utm_tag_data_collection_table
    from .wizard import create_wizard_table

    create_question_group_table(logger)
    create_question_table(logger)
    create_wizard_table(logger)
    create_place_table(logger)
    create_contact_profile_table(logger)
    create_contact_request_table(logger)
    create_corporation_profile_table(logger)
    create_attribute_value_table(logger)
    create_activity_history_table(logger)
    create_utm_tag_data_collection_table(logger)

    return


def _get_question_group(endpoint_id: str, question_group_uuid: str) -> Dict[str, Any]:
    from .question_group import get_question_group

    question_group = get_question_group(endpoint_id, question_group_uuid)
    return {
        "question_group_uuid": question_group.question_group_uuid,
        "question_group_name": question_group.question_group_name,
        "question_group_description": question_group.question_group_description,
        "region": question_group.region,
        "question_criteria": question_group.question_criteria,
        "weight": question_group.weight,
    }


def _get_questions(endpoint_id: str, wizard_uuid: str) -> Dict[str, Any]:
    from .question import QuestionModel

    results = QuestionModel.query(
        hash_key=endpoint_id,
        range_key_condition=None,
        filter_condition=(QuestionModel.wizard_uuid == wizard_uuid),
    )

    questions = [
        {
            "question_uuid": result.question_uuid,
            "data_type": result.data_type,
            "question": result.question,
            "priority": result.priority,
            "attribute_name": result.attribute_name,
            "attribute_type": result.attribute_type,
            "option_values": result.option_values,
            "condition": result.condition,
        }
        for result in results
    ]

    return questions


def _get_wizards(endpoint_id: str, question_group_uuid: str) -> Dict[str, Any]:
    from .wizard import WizardModel

    results = WizardModel.query(
        hash_key=endpoint_id,
        range_key_condition=None,
        filter_condition=(WizardModel.question_group_uuid == question_group_uuid),
    )

    wizards = [
        {
            "wizard_uuid": result.wizard_uuid,
            "wizard_title": result.wizard_title,
            "wizard_description": result.wizard_description,
            "wizard_type": result.wizard_type,
            "form_schema": result.form_schema,
            "embed_content": result.embed_content,
            "priority": result.priority,
            "questions": _get_questions(endpoint_id, result.wizard_uuid),
        }
        for result in results
    ]

    return wizards


def _get_wizard(endpoint_id: str, wizard_uuid: str) -> Dict[str, Any]:
    from .wizard import get_wizard

    wizard = get_wizard(endpoint_id, wizard_uuid)
    return {
        "wizard_uuid": wizard.wizard_uuid,
        "question_group": _get_question_group(
            wizard.endpoint_id, wizard.question_group_uuid
        ),
        "wizard_title": wizard.wizard_title,
        "wizard_description": wizard.wizard_description,
        "wizard_type": wizard.wizard_type,
        "form_schema": wizard.form_schema,
        "embed_content": wizard.embed_content,
        "priority": wizard.priority,
    }


def _get_place(region: str, place_uuid: str) -> Dict[str, Any]:
    from .place import get_place

    place = get_place(region, place_uuid)
    return {
        "region": place.region,
        "place_uuid": place.place_uuid,
        "business_name": place.business_name,
        "latitude": place.latitude,
        "longitude": place.longitude,
        "address": place.address,
        "website": place.website,
        "types": place.types,
        "phone_number": place.phone_number,
        "corporation_profile": (
            _get_corporation_profile(place.endpoint_id, place.corporation_uuid)
            if place.corporation_uuid is not None
            else None
        ),
    }


def _get_corporation_profile(endpoint_id: str, corporation_uuid: str) -> Dict[str, Any]:
    from .corporation_profile import get_corporation_profile

    corporation_profile = get_corporation_profile(endpoint_id, corporation_uuid)
    return {
        "corporation_uuid": corporation_profile.corporation_uuid,
        "external_id": corporation_profile.external_id,
        "corporation_type": corporation_profile.corporation_type,
        "business_name": corporation_profile.business_name,
        "categories": corporation_profile.categories,
        "address": corporation_profile.address,
    }


def _get_contact_profile(place_uuid: str, contact_uuid: str) -> Dict[str, Any]:
    from .contact_profile import get_contact_profile

    contact_profile = get_contact_profile(place_uuid, contact_uuid)
    return {
        "contact_uuid": contact_profile.contact_uuid,
        "place": _get_place(contact_profile.endpoint_id, contact_profile.place_uuid),
        "email": contact_profile.email,
        "first_name": contact_profile.first_name,
        "last_name": contact_profile.last_name,
    }
