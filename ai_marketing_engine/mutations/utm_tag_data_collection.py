#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import traceback
from typing import Any, Dict

from graphene import Boolean, Field, Mutation, String

from ..models.utm_tag_data_collection import (
    delete_utm_tag_data_collection,
    insert_utm_tag_data_collection,
)
from ..types.utm_tag_data_collection import UtmTagDataCollectionType


class InsertUtmTagDataCollection(Mutation):
    utm_tag_data_collection = Field(UtmTagDataCollectionType)

    class Arguments:
        tag_name = String(required=True)
        place_uuid = String(required=True)
        contact_uuid = String(required=True)
        keyword = String(required=True)
        utm_campaign = String(required=True)
        utm_content = String(required=True)
        utm_medium = String(required=True)
        utm_source = String(required=True)
        utm_term = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUtmTagDataCollection":
        try:
            utm_tag_data_collection = insert_utm_tag_data_collection(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUtmTagDataCollection(
            utm_tag_data_collection=utm_tag_data_collection
        )


class DeleteUtmTagDataCollection(Mutation):
    ok = Boolean()

    class Arguments:
        collection_uuid = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteUtmTagDataCollection":
        try:
            ok = delete_utm_tag_data_collection(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteUtmTagDataCollection(ok=ok)
