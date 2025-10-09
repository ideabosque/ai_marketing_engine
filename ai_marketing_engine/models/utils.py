# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
from typing import Any, Dict, List

from graphene import ResolveInfo


def _initialize_tables(logger: logging.Logger) -> None:
    from .activity_history import create_activity_history_table
    from .attribute_value import create_attribute_value_table
    from .contact_profile import create_contact_profile_table
    from .contact_request import create_contact_request_table
    from .corporation_profile import create_corporation_profile_table
    from .place import create_place_table
    from .question_group import create_question_group_table
    from .utm_tag_data_collection import create_utm_tag_data_collection_table

    create_question_group_table(logger)
    create_place_table(logger)
    create_contact_profile_table(logger)
    create_contact_request_table(logger)
    create_corporation_profile_table(logger)
    create_attribute_value_table(logger)
    create_activity_history_table(logger)
    create_utm_tag_data_collection_table(logger)

    return


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
    from .contact_profile import get_contact_profile, get_contact_profile_count

    try:
        assert (
            get_contact_profile_count(place_uuid=place_uuid, contact_uuid=contact_uuid)
            == 1
        ), "Contact profile not found."
    except AssertionError as e:
        return {}

    contact_profile = get_contact_profile(place_uuid, contact_uuid)
    return {
        "contact_uuid": contact_profile.contact_uuid,
        "place": _get_place(contact_profile.endpoint_id, contact_profile.place_uuid),
        "email": contact_profile.email,
        "first_name": contact_profile.first_name,
        "last_name": contact_profile.last_name,
    }


def _insert_update_attribute_values(
    info: ResolveInfo,
    data_type: str,
    data_identity: str,
    updated_by: str,
    data: Dict[str, Any] = {},
) -> Dict[str, Any]:
    from .attribute_value import (
        _get_active_attribute_value,
        insert_update_attribute_value,
    )

    # Insert/update attribute values
    attribute_values = []
    for attribute_name, value in data.items():
        active_attribute_value = _get_active_attribute_value(
            f"{data_type}-{attribute_name}", data_identity
        )
        if active_attribute_value and active_attribute_value.value == value:
            attribute_values.append(active_attribute_value)
            continue

        attribute_value = insert_update_attribute_value(
            info,
            **{
                "data_type_attribute_name": f"{data_type}-{attribute_name}",
                "data_identity": data_identity,
                "value": value,
                "updated_by": updated_by,
            },
        )
        attribute_values.append(attribute_value)

    return {
        attribute_value.data_type_attribute_name.split("-")[1]: attribute_value.value
        for attribute_value in attribute_values
    }


def _get_data(
    endpoint_id: str,
    data_identity: str,
    data_type: str,
) -> Dict[str, Any]:
    from .attribute_value import AttributeValueModel

    results = AttributeValueModel.data_identity_data_type_attribute_name_index.query(
        hash_key=data_identity,
        range_key_condition=AttributeValueModel.data_type_attribute_name.startswith(
            data_type
        ),
        filter_condition=(
            (AttributeValueModel.status == "active")
            & (AttributeValueModel.endpoint_id == endpoint_id)
        ),
    )

    return {
        result.data_type_attribute_name.split("-")[1]: result.value
        for result in results
    }
