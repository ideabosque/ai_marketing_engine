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
    endpoint_id: str,
    data_identity: str,
    data_type: str,
) -> Dict[str, Any]:
    from .attribute_value import get_attributes_data

    return get_attributes_data(endpoint_id, data_identity, data_type)
