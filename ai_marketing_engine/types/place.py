#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, Field, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType

from ..models.batch_loaders import get_loaders
from .corporation_profile import CorporationProfileType


class PlaceType(ObjectType):
    endpoint_id = String()
    place_uuid = String()
    region = String()
    latitude = String()
    longitude = String()
    business_name = String()
    address = String()
    phone_number = String()
    website = String()
    types = List(String)

    # Nested resolver: strongly-typed nested relationship
    corporation_uuid = String()  # keep raw id
    corporation_profile = Field(lambda: CorporationProfileType)

    updated_by = String()
    updated_at = DateTime()
    created_at = DateTime()

    # ------- Nested resolvers -------

    def resolve_corporation_profile(parent, info):
        """
        Resolve nested corporation profile.

        Works in two cases:
        1) Place came from get_place_type -> has corporation_uuid
        2) Place came from _get_place -> already has corporation_profile dict
        """
        # Case 2: already embedded (e.g., via _get_place)
        existing = getattr(parent, "corporation_profile", None)
        if isinstance(existing, dict):
            return CorporationProfileType(**existing)
        if isinstance(existing, CorporationProfileType):
            return existing

        # Case 1: need to fetch by endpoint_id + corporation_uuid
        endpoint_id = getattr(parent, "endpoint_id", None)
        corporation_uuid = getattr(parent, "corporation_uuid", None)
        if not endpoint_id or not corporation_uuid:
            return None

        loaders = get_loaders(info.context)
        return loaders.corporation_loader.load((endpoint_id, corporation_uuid)).then(
            lambda corp_dict: CorporationProfileType(**corp_dict)
            if corp_dict
            else None
        )


class PlaceListType(ListObjectType):
    place_list = List(PlaceType)
