#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import DateTime, Field, List, ObjectType, String

from silvaengine_dynamodb_base import ListObjectType

from ..models.batch_loaders import get_loaders
from .contact_profile import ContactProfileType


class ContactRequestType(ObjectType):
    endpoint_id = String()
    request_uuid = String()
    request_title = String()
    request_detail = String()

    # Nested resolver: strongly-typed nested relationship
    contact_uuid = String()  # keep raw id
    place_uuid = String()     # keep raw id
    contact_profile = Field(lambda: ContactProfileType)

    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()

    # ------- Nested resolvers -------

    def resolve_contact_profile(parent, info):
        """
        Resolve nested contact profile.

        Works in two cases:
        1) ContactRequest came from get_contact_request_type -> has contact_uuid
        2) ContactRequest came from elsewhere -> already has contact_profile dict
        """
        # Case 2: already embedded
        existing = getattr(parent, "contact_profile", None)
        if isinstance(existing, dict):
            return ContactProfileType(**existing)
        if isinstance(existing, ContactProfileType):
            return existing

        # Case 1: need to fetch by endpoint_id + contact_uuid
        endpoint_id = getattr(parent, "endpoint_id", None)
        contact_uuid = getattr(parent, "contact_uuid", None)
        if not endpoint_id or not contact_uuid:
            return None

        loaders = get_loaders(info.context)
        return loaders.contact_profile_loader.load((endpoint_id, contact_uuid)).then(
            lambda contact_dict: ContactProfileType(**contact_dict)
            if contact_dict
            else None
        )


class ContactRequestListType(ListObjectType):
    contact_request_list = List(ContactRequestType)
