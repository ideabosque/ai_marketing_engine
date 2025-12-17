# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
from typing import Any, Dict

from graphene import ResolveInfo


def _initialize_tables(logger: logging.Logger) -> None:
    from .activity_history import create_activity_history_table
    from .attribute_value import create_attribute_value_table
    from .contact_profile import create_contact_profile_table
    from .contact_request import create_contact_request_table
    from .corporation_profile import create_corporation_profile_table
    from .place import create_place_table

    create_place_table(logger)
    create_contact_profile_table(logger)
    create_contact_request_table(logger)
    create_corporation_profile_table(logger)
    create_attribute_value_table(logger)
    create_activity_history_table(logger)

    return


def _get_place(partition_key: str, place_uuid: str) -> Dict[str, Any]:
    from .place import get_place, get_place_count

    try:
        assert (
            place_uuid is not None
            and get_place_count(partition_key=partition_key, place_uuid=place_uuid) == 1
        ), "Place not found."
    except AssertionError as e:
        return {}

    place = get_place(partition_key, place_uuid)
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
            _get_corporation_profile(place.partition_key, place.corporation_uuid)
            if place.corporation_uuid is not None
            else None
        ),
    }


def _get_corporation_profile(
    partition_key: str, corporation_uuid: str
) -> Dict[str, Any]:
    from .corporation_profile import (
        get_corporation_profile,
        get_corporation_profile_count,
    )

    try:
        assert (
            corporation_uuid is not None
            and get_corporation_profile_count(
                partition_key=partition_key, corporation_uuid=corporation_uuid
            )
            == 1
        ), "Corporation profile not found."
    except AssertionError as e:
        return {}

    corporation_profile = get_corporation_profile(partition_key, corporation_uuid)
    return {
        "corporation_uuid": corporation_profile.corporation_uuid,
        "external_id": corporation_profile.external_id,
        "corporation_type": corporation_profile.corporation_type,
        "business_name": corporation_profile.business_name,
        "categories": corporation_profile.categories,
        "address": corporation_profile.address,
    }


def _get_contact_profile(partition_key: str, contact_uuid: str) -> Dict[str, Any]:
    from .contact_profile import get_contact_profile, get_contact_profile_count

    try:
        assert (
            contact_uuid is not None
            and get_contact_profile_count(
                partition_key=partition_key, contact_uuid=contact_uuid
            )
            == 1
        ), "Contact profile not found."
    except AssertionError as e:
        return {}

    contact_profile = get_contact_profile(partition_key, contact_uuid)
    return {
        "place": _get_place(contact_profile.partition_key, contact_profile.place_uuid),
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
    from .attribute_value import insert_update_attribute_values

    params = {
        "data_type": data_type,
        "data_identity": data_identity,
        "data": data,
        "updated_by": updated_by,
    }
    return insert_update_attribute_values(info, **params)


def _get_data(
    partition_key: str,
    data_identity: str,
    data_type: str,
) -> Dict[str, Any]:
    from .attribute_value import get_attributes_data

    return get_attributes_data(partition_key, data_identity, data_type)
