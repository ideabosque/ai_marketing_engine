#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import time
from typing import Any, Dict

from graphene import Field, Int, List, ObjectType, ResolveInfo, String

from silvaengine_utility import JSON

from .mutations.activity_history import DeleteActivityHistory, InsertActivityHistory
from .mutations.attribute_value import DeleteAttributeValue, InsertUpdateAttributeValue
from .mutations.contact_profile import DeleteContactProfile, InsertUpdateContactProfile
from .mutations.contact_request import DeleteContactRequest, InsertUpdateContactRequest
from .mutations.corporation_profile import (
    DeleteCorporationProfile,
    InsertUpdateCorporationProfile,
)
from .mutations.place import DeletePlace, InsertUpdatePlace
from .mutations.question import DeleteQuestion, InsertUpdateQuestion
from .mutations.question_group import DeleteQuestionGroup, InsertUpdateQuestionGroup
from .mutations.utm_tag_data_collection import (
    DeleteUtmTagDataCollection,
    InsertUtmTagDataCollection,
)
from .mutations.wizard import DeleteWizard, InsertUpdateWizard
from .queries.activity_history import (
    resolve_activity_history,
    resolve_activity_history_list,
)
from .queries.ai_marketing import resolve_crm_user_list, resolve_presigned_upload_url
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
from .queries.question import resolve_question, resolve_question_list
from .queries.question_group import resolve_question_group, resolve_question_group_list
from .queries.utm_tag_data_collection import (
    resolve_utm_tag_data_collection,
    resolve_utm_tag_data_collection_list,
)
from .queries.wizard import resolve_wizard, resolve_wizard_list
from .types.activity_history import ActivityHistoryListType, ActivityHistoryType
from .types.ai_marketing import CrmUserListType, PresignedUploadUrlType
from .types.attribute_value import AttributeValueListType, AttributeValueType
from .types.contact_profile import ContactProfileListType, ContactProfileType
from .types.contact_request import ContactRequestListType, ContactRequestType
from .types.corporation_profile import (
    CorporationProfileListType,
    CorporationProfileType,
)
from .types.place import PlaceListType, PlaceType
from .types.question import QuestionListType, QuestionType
from .types.question_group import QuestionGroupListType, QuestionGroupType
from .types.utm_tag_data_collection import (
    UtmTagDataCollectionListType,
    UtmTagDataCollectionType,
)
from .types.wizard import WizardListType, WizardType


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
        QuestionGroupListType,
        QuestionGroupType,
        QuestionListType,
        QuestionType,
        UtmTagDataCollectionListType,
        UtmTagDataCollectionType,
        ContactRequestType,
        ContactRequestListType,
        WizardListType,
        WizardType,
        PresignedUploadUrlType,
        CrmUserListType,
    ]


class Query(ObjectType):
    ping = String()

    presigned_upload_url = Field(
        PresignedUploadUrlType,
        required=True,
        object_key=String(required=True),
    )

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

    question = Field(
        QuestionType,
        required=True,
        question_uuid=String(required=True),
    )

    question_list = Field(
        QuestionListType,
        page_number=Int(),
        limit=Int(),
        data_type=String(),
        question=String(),
        attribute_name=String(),
        attribute_type=String(),
    )

    wizard = Field(
        WizardType,
        required=True,
        wizard_uuid=String(required=True),
    )

    wizard_list = Field(
        WizardListType,
        page_number=Int(),
        limit=Int(),
        wizard_title=String(),
        wizard_description=String(),
        priority=Int(),
        wizard_types=List(String),
    )

    question_group = Field(
        QuestionGroupType,
        required=True,
        question_group_uuid=String(required=True),
    )

    question_group_list = Field(
        QuestionGroupListType,
        page_number=Int(),
        limit=Int(),
        region=String(),
        question_criteria=JSON(),
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
        place_uuid=String(required=True),
        contact_uuid=String(required=True),
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

    utm_tag_data_collection = Field(
        UtmTagDataCollectionType,
        required=True,
        collection_uuid=String(required=True),
    )

    utm_tag_data_collection_list = Field(
        UtmTagDataCollectionListType,
        page_number=Int(),
        limit=Int(),
        tag_name=String(),
        place_uuids=List(String),
        contact_uuids=List(String),
        keyword=String(),
    )

    crm_user_list = Field(
        CrmUserListType,
        page_number=Int(),
        limit=Int(),
        address=String(),
    )

    def resolve_ping(self, info: ResolveInfo) -> str:
        return f"Hello at {time.strftime('%X')}!!"

    def resolve_presigned_upload_url(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> PresignedUploadUrlType:
        return resolve_presigned_upload_url(info, **kwargs)

    def resolve_activity_history(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> ActivityHistoryType:
        return resolve_activity_history(info, **kwargs)

    def resolve_activity_history_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> ActivityHistoryListType:
        return resolve_activity_history_list(info, **kwargs)

    def resolve_question(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> QuestionType:
        return resolve_question(info, **kwargs)

    def resolve_question_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> QuestionListType:
        return resolve_question_list(info, **kwargs)

    def resolve_wizard(self, info: ResolveInfo, **kwargs: Dict[str, Any]) -> WizardType:
        return resolve_wizard(info, **kwargs)

    def resolve_wizard_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> WizardListType:
        return resolve_wizard_list(info, **kwargs)

    def resolve_question_group(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> QuestionGroupType:
        return resolve_question_group(info, **kwargs)

    def resolve_question_group_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> QuestionGroupListType:
        return resolve_question_group_list(info, **kwargs)

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

    def resolve_utm_tag_data_collection(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> UtmTagDataCollectionType:
        return resolve_utm_tag_data_collection(info, **kwargs)

    def resolve_utm_tag_data_collection_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> UtmTagDataCollectionListType:
        return resolve_utm_tag_data_collection_list(info, **kwargs)

    def resolve_attribute_value(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> AttributeValueType:
        return resolve_attribute_value(info, **kwargs)

    def resolve_attribute_value_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> AttributeValueListType:
        return resolve_attribute_value_list(info, **kwargs)

    def resolve_crm_user_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CrmUserListType:
        return resolve_crm_user_list(info, **kwargs)


class Mutations(ObjectType):
    insert_activity_history = InsertActivityHistory.Field()
    delete_activity_history = DeleteActivityHistory.Field()
    insert_update_question_group = InsertUpdateQuestionGroup.Field()
    delete_question_group = DeleteQuestionGroup.Field()
    insert_update_wizard = InsertUpdateWizard.Field()
    delete_wizard = DeleteWizard.Field()
    insert_update_question = InsertUpdateQuestion.Field()
    delete_question = DeleteQuestion.Field()
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
    insert_utm_tag_data_collection = InsertUtmTagDataCollection.Field()
    delete_utm_tag_data_collection = DeleteUtmTagDataCollection.Field()
