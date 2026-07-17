# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
from typing import Any, Dict, List

from graphene import ResolveInfo


def initialize_tables(logger: logging.Logger) -> None:
    """
    Initialize all database tables if they don't exist.
    Called during Config.initialize() when initialize_tables=True.
    """
    from .activity_history import ActivityHistoryModel
    from .attribute_value import AttributeValueModel
    from .contact_profile import ContactProfileModel
    from .contact_request import ContactRequestModel
    from .corporation_profile import CorporationProfileModel
    from .place import PlaceModel

    models: List = [
        PlaceModel,
        ContactProfileModel,
        ContactRequestModel,
        CorporationProfileModel,
        AttributeValueModel,
        ActivityHistoryModel,
    ]

    for model in models:
        if model.exists():
            continue

        table_name = model.Meta.table_name
        # Create with on-demand billing (PAY_PER_REQUEST)
        model.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        logger.info(f"The {table_name} table has been created.")


def insert_update_attribute_values(
    info: ResolveInfo,
    data_type: str,
    data_identity: str,
    updated_by: str,
    data: Dict[str, Any] = {},
    partition_key: str = None,
) -> Dict[str, Any]:
    """
    Insert or update attribute values for an entity.
    Used by model insert/update functions.
    """
    from .attribute_value import insert_update_attribute_values as _insert_update_attrs

    params = {
        "data_type": data_type,
        "data_identity": data_identity,
        "data": data,
        "updated_by": updated_by,
    }
    if partition_key:
        params["partition_key"] = partition_key
    return _insert_update_attrs(info, **params)


def get_data(
    partition_key: str,
    data_identity: str,
    data_type: str,
) -> Dict[str, Any]:
    """
    Get attribute data for an entity.
    Used by attribute data loaders.
    """
    from .attribute_value import get_attributes_data

    return get_attributes_data(partition_key, data_identity, data_type)
