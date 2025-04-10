# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
from typing import Any, Dict, List


def _initialize_tables(logger: logging.Logger) -> None:
    from .question_group import create_question_group_table

    create_question_group_table(logger)


def _get_question_group(endpoint_id: str, question_group_uuid: str) -> Dict[str, Any]:
    from .question_group import get_question_group

    question_group = get_question_group(endpoint_id, question_group_uuid)
    return {
        "endpoint_id": question_group.endpoint_id,
        "question_group_uuid": question_group.question_group_uuid,
        "question_group_name": question_group.question_group_name,
        "question_group_description": question_group.question_group_description,
        "region": question_group.region,
        "question_criteria": question_group.question_criteria,
        "weight": question_group.weight,
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
    }


def _get_corporation_profile(endpoint_id: str, corporation_uuid: str) -> Dict[str, Any]:
    from .corporation_profile import get_corporation_profile

    corporation_profile = get_corporation_profile(endpoint_id, corporation_uuid)
    return {
        "corporation_uuid": corporation_profile.corporation_uuid,
        "external_id": corporation_profile.external_id,
        "corportation_type": corporation_profile.corportation_type,
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
        "corporation_profile": (
            _get_corporation_profile(
                contact_profile.endpoint_id, contact_profile.corporation_uuid
            )
            if contact_profile.corporation_uuid is not None
            else None
        ),
    }
