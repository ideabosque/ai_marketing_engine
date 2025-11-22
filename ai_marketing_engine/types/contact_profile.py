#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, Field, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON

from ..models.utils import _get_data, _get_place
from .place import PlaceType


class ContactProfileType(ObjectType):
    endpoint_id = String()
    contact_uuid = String()
    email = String()
    first_name = String()
    last_name = String()

    # Nested resolver: strongly-typed nested place
    place_uuid = String()
    place = Field(lambda: PlaceType)

    # Dynamic attributes for contact – keep as JSON, resolved lazily
    data = JSON()

    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()

    # ------- Nested resolvers -------

    def resolve_place(parent, info):
        """
        Resolve nested Place for this contact_profile.
        Uses utils._get_place so existing behavior is preserved.
        """
        endpoint_id = getattr(parent, "endpoint_id", None)
        place_uuid = getattr(parent, "place_uuid", None)
        if not endpoint_id or not place_uuid:
            return None

        place_dict = _get_place(endpoint_id, place_uuid)
        if not place_dict:
            return None

        # Wrap dict into PlaceType so its own nested resolvers work
        return PlaceType(**place_dict)

    def resolve_data(parent, info):
        """
        Resolve dynamic attributes for contact profiles on demand.
        Uses AttributeValueModel via _get_data(..., "contact").
        """
        endpoint_id = getattr(parent, "endpoint_id", None)
        contact_uuid = getattr(parent, "contact_uuid", None)
        if not endpoint_id or not contact_uuid:
            return None

        return _get_data(endpoint_id, contact_uuid, "contact")


class ContactProfileListType(ListObjectType):
    contact_profile_list = List(ContactProfileType)
