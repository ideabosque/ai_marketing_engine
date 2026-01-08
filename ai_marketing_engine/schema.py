#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import time
from typing import Any, Dict

from graphene import Field, Int, List, ObjectType, ResolveInfo, String

from .mutations.activity_history import DeleteActivityHistory, InsertActivityHistory
from .mutations.attribute_value import DeleteAttributeValue, InsertUpdateAttributeValue
from .mutations.contact_profile import DeleteContactProfile, InsertUpdateContactProfile
from .mutations.contact_request import DeleteContactRequest, InsertUpdateContactRequest
from .mutations.corporation_profile import (
    DeleteCorporationProfile,
    InsertUpdateCorporationProfile,
)
from .mutations.place import DeletePlace, InsertUpdatePlace
from .queries.activity_history import (
    resolve_activity_history,
    resolve_activity_history_list,
)
from .queries.ai_marketing import resolve_presigned_upload_url

# from .queries.ai_marketing import resolve_crm_user_list, resolve_presigned_upload_url
from .queries.attribute_value import (
    resolve_attribute_value,
    resolve_attribute_value_list,
)
from .queries.contact_profile import (
    resolve_contact_profile,
    resolve_contact_profile_list,
)
from .queries.contact_request import (
    resolve_contact_request,
    resolve_contact_request_list,
)
from .queries.corporation_profile import (
    resolve_corporation_profile,
    resolve_corporation_profile_list,
)
from .queries.place import resolve_place, resolve_place_list
from .types.activity_history import ActivityHistoryListType, ActivityHistoryType
from .types.ai_marketing import PresignedUploadUrlType
from .types.attribute_value import AttributeValueListType, AttributeValueType
from .types.contact_profile import ContactProfileListType, ContactProfileType
from .types.contact_request import ContactRequestListType, ContactRequestType
from .types.corporation_profile import (
    CorporationProfileListType,
    CorporationProfileType,
)
from .types.place import PlaceListType, PlaceType


def type_class():
    return [
        AttributeValueType,
        AttributeValueListType,
        CorporationProfileListType,
        CorporationProfileType,
        CorporationProfileListType,
        CorporationProfileType,
        ContactProfileListType,
        ContactProfileType,
        ContactProfileListType,
        ContactProfileType,
        PlaceListType,
        PlaceType,
        ContactRequestType,
        ContactRequestListType,
        PresignedUploadUrlType,
    ]


class Query(ObjectType):
    ping = String()

    def resolve_presigned_upload_url(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> PresignedUploadUrlType:
        return resolve_presigned_upload_url(info, **kwargs)

    activity_history = Field(
        ActivityHistoryType,
        required=True,
        id=String(required=True),
        timestamp=Int(required=True),
    )

    activity_history_list = Field(
        ActivityHistoryListType,
        page_number=Int(),
        limit=Int(),
        id=String(),
        activity_type=String(),
        activity_types=List(String),
        log=String(),
    )

    place = Field(
        PlaceType,
        required=True,
        place_uuid=String(required=True),
    )

    place_list = Field(
        PlaceListType,
        page_number=Int(),
        limit=Int(),
        region=String(),
        latitude=String(),
        longitude=String(),
        business_name=String(),
        address=String(),
        website=String(),
        corporation_uuid=String(),
    )

    contact_profile = Field(
        ContactProfileType,
        required=True,
        email=String(required=False),
        contact_uuid=String(required=False),
    )

    contact_profile_list = Field(
        ContactProfileListType,
        page_number=Int(),
        limit=Int(),
        place_uuid=String(),
        email=String(),
        first_name=String(),
        last_name=String(),
    )

    contact_request = Field(
        ContactRequestType,
        required=True,
        contact_uuid=String(required=True),
        request_uuid=String(required=True),
    )

    contact_request_list = Field(
        ContactRequestListType,
        page_number=Int(),
        limit=Int(),
        contact_uuid=String(),
        request_title=String(),
        request_detail=String(),
        place_uuid=String(),
    )

    corporation_profile = Field(
        CorporationProfileType,
        required=True,
        corporation_uuid=String(required=True),
    )

    corporation_profile_list = Field(
        CorporationProfileListType,
        page_number=Int(),
        limit=Int(),
        corporation_type=String(),
        external_id=String(),
        business_name=String(),
        category=String(),
        address=String(),
    )

    attribute_value = Field(
        AttributeValueType,
        required=True,
        data_type_attribute_name=String(required=True),
        value_version_uuid=String(required=True),
    )

    attribute_value_list = Field(
        AttributeValueListType,
        page_number=Int(),
        limit=Int(),
        data_type_attribute_name=String(),
        data_identity=String(),
        value=String(),
        statuses=List(String),
    )

    def resolve_ping(self, info: ResolveInfo) -> str:
        return f"Hello at {time.strftime('%X')}!!"

    def resolve_activity_history(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> ActivityHistoryType:
        return resolve_activity_history(info, **kwargs)

    def resolve_activity_history_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> ActivityHistoryListType:
        return resolve_activity_history_list(info, **kwargs)

    def resolve_place(self, info: ResolveInfo, **kwargs: Dict[str, Any]) -> PlaceType:
        return resolve_place(info, **kwargs)

    def resolve_place_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> PlaceListType:
        return resolve_place_list(info, **kwargs)

    def resolve_contact_profile(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> ContactProfileType:
        return resolve_contact_profile(info, **kwargs)

    def resolve_contact_profile_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> ContactProfileListType:
        return resolve_contact_profile_list(info, **kwargs)

    def resolve_contact_request(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> ContactRequestType:
        return resolve_contact_request(info, **kwargs)

    def resolve_contact_request_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> ContactRequestListType:
        return resolve_contact_request_list(info, **kwargs)

    def resolve_corporation_profile(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CorporationProfileType:
        return resolve_corporation_profile(info, **kwargs)

    def resolve_corporation_profile_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CorporationProfileListType:
        return resolve_corporation_profile_list(info, **kwargs)

    def resolve_attribute_value(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> AttributeValueType:
        return resolve_attribute_value(info, **kwargs)

    def resolve_attribute_value_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> AttributeValueListType:
        return resolve_attribute_value_list(info, **kwargs)

    # def resolve_crm_user_list(
    #     self, info: ResolveInfo, **kwargs: Dict[str, Any]
    # ) -> CrmUserListType:
    #     return resolve_crm_user_list(info, **kwargs)


class Mutations(ObjectType):
    insert_activity_history = InsertActivityHistory.Field()
    delete_activity_history = DeleteActivityHistory.Field()
    insert_update_place = InsertUpdatePlace.Field()
    delete_place = DeletePlace.Field()
    insert_update_corporation_profile = InsertUpdateCorporationProfile.Field()
    delete_corporation_profile = DeleteCorporationProfile.Field()
    insert_update_contact_profile = InsertUpdateContactProfile.Field()
    delete_contact_profile = DeleteContactProfile.Field()
    insert_update_contact_request = InsertUpdateContactRequest.Field()
    delete_contact_request = DeleteContactRequest.Field()
    insert_update_attribute_value = InsertUpdateAttributeValue.Field()
    delete_attribute_value = DeleteAttributeValue.Field()
