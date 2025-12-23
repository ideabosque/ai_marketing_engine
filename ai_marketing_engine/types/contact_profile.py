#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, Field, List, ObjectType, String
from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON

from ..models.batch_loaders import get_loaders
from .place import PlaceType


class ContactProfileType(ObjectType):
    partition_key = String()
    contact_uuid = String()
    email = String()
    endpoint_id = String()
    part_id = String()
    first_name = String()
    last_name = String()

    # Nested resolver: strongly-typed nested place
    place_uuid = String()
    place = Field(lambda: PlaceType)

    # Dynamic attributes for contact – keep as JSON, resolved lazily
    data = Field(JSON)

    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()

    # ------- Nested resolvers -------

    def resolve_place(parent, info):
        """
        Resolve nested Place for this contact_profile.
        Uses request-scoped DataLoader to avoid N+1 fetches when resolving lists.
        """
        existing_place = getattr(parent, "place", None)
        if isinstance(existing_place, dict):
            return PlaceType(**existing_place)
        if isinstance(existing_place, PlaceType):
            return existing_place

        partition_key = getattr(parent, "partition_key", None) or getattr(
            parent, "endpoint_id", None
        )
        place_uuid = getattr(parent, "place_uuid", None)
        if not partition_key or not place_uuid:
            return None

        loaders = get_loaders(info.context)
        return loaders.place_loader.load((partition_key, place_uuid)).then(
            lambda place_dict: PlaceType(**place_dict) if place_dict else None
        )

    def resolve_data(parent, info):
        """
        Resolve dynamic attributes for contact profiles on demand.
        Uses AttributeValueModel via _get_data(..., "contact").
        """
        existing_data = getattr(parent, "data", None)
        if isinstance(existing_data, dict):
            return existing_data

        partition_key = getattr(parent, "partition_key", None) or getattr(
            parent, "endpoint_id", None
        )
        contact_uuid = getattr(parent, "contact_uuid", None)
        if not partition_key or not contact_uuid:
            return None

        loaders = get_loaders(info.context)
        return loaders.contact_data_loader.load((partition_key, contact_uuid))


class ContactProfileListType(ListObjectType):
    contact_profile_list = List(ContactProfileType)
