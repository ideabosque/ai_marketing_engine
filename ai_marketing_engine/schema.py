#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import time
from typing import Any, Dict

from graphene import (
    Boolean,
    DateTime,
    Field,
    Int,
    List,
    ObjectType,
    ResolveInfo,
    String,
)

from silvaengine_utility import JSON

from .mutations import (
    DeleteActivityHistory,
    DeleteCompanyContactProfile,
    DeleteCompanyContactRequest,
    DeleteCompanyCorporationProfile,
    DeleteContactChatbotHistory,
    DeleteContactProfile,
    DeleteCorporationPlace,
    DeleteCorporationProfile,
    DeletePlace,
    DeleteQuestion,
    DeleteQuestionCriteria,
    DeleteUtmTagDataCollection,
    InsertActivityHistory,
    InsertContactChatbotHistory,
    InsertUpdateCompanyContactProfile,
    InsertUpdateCompanyContactRequest,
    InsertUpdateCompanyCorporationProfile,
    InsertUpdateContactProfile,
    InsertUpdateCorporationPlace,
    InsertUpdateCorporationProfile,
    InsertUpdatePlace,
    InsertUpdateQuestion,
    InsertUpdateQuestionCriteria,
    InsertUtmTagDataCollection,
)
from .queries import (
    resolve_activity_history,
    resolve_activity_history_list,
    resolve_company_contact_profile,
    resolve_company_contact_profile_list,
    resolve_company_contact_request,
    resolve_company_contact_request_list,
    resolve_company_corporation_profile,
    resolve_company_corporation_profile_list,
    resolve_contact_chatbot_history,
    resolve_contact_chatbot_history_list,
    resolve_contact_profile,
    resolve_contact_profile_list,
    resolve_corporation_place,
    resolve_corporation_place_list,
    resolve_corporation_profile,
    resolve_corporation_profile_list,
    resolve_place,
    resolve_place_list,
    resolve_question,
    resolve_question_criteria,
    resolve_question_criteria_list,
    resolve_question_list,
    resolve_utm_tag_data_collection,
    resolve_utm_tag_data_collection_list,
)
from .types import (
    ActivityHistoryListType,
    ActivityHistoryType,
    CompanyContactProfileListType,
    CompanyContactProfileType,
    CompanyContactRequestListType,
    CompanyContactRequestType,
    CompanyCorporationProfileListType,
    CompanyCorporationProfileType,
    ContactChatbotHistoryListType,
    ContactChatbotHistoryType,
    ContactProfileListType,
    ContactProfileType,
    CorporationPlaceListType,
    CorporationPlaceType,
    CorporationProfileListType,
    CorporationProfileType,
    PlaceListType,
    PlaceType,
    QuestionCriteriaListType,
    QuestionCriteriaType,
    QuestionListType,
    QuestionType,
    UtmTagDataCollectionListType,
    UtmTagDataCollectionType,
)


def type_class():
    return [
        CorporationPlaceListType,
        CorporationPlaceType,
        CompanyCorporationProfileListType,
        CompanyCorporationProfileType,
        CorporationProfileListType,
        CorporationProfileType,
        ContactChatbotHistoryListType,
        ContactChatbotHistoryType,
        CompanyContactProfileListType,
        CompanyContactProfileType,
        ContactProfileListType,
        ContactProfileType,
        PlaceListType,
        PlaceType,
        QuestionListType,
        QuestionType,
        UtmTagDataCollectionListType,
        UtmTagDataCollectionType,
        CompanyContactRequestType,
        CompanyContactRequestListType,
    ]


class Query(ObjectType):
    ping = String()

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
        question_groups=List(String),
        question=String(),
        attribute=String(),
        attribute_type=String(),
    )

    question_criteria = Field(
        QuestionCriteriaType,
        required=True,
        question_group=String(required=True),
    )

    question_criteria_list = Field(
        QuestionCriteriaListType,
        page_number=Int(),
        limit=Int(),
        region=String(),
        question_criteria=JSON(),
    )

    place = Field(
        PlaceType,
        required=True,
        region=String(required=True),
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
        regions=List(String),
        first_name=String(),
        last_name=String(),
    )

    company_contact_profile = Field(
        CompanyContactProfileType,
        required=True,
        contact_uuid=String(required=True),
    )

    company_contact_profile_list = Field(
        CompanyContactProfileListType,
        page_number=Int(),
        limit=Int(),
        email=String(),
        place_uuid=String(),
        corporation_types=List(String),
    )

    company_contact_request = Field(
        CompanyContactRequestType,
        required=True,
        contact_uuid=String(required=True),
        request_uuid=String(required=True),
    )

    company_contact_request_list = Field(
        CompanyContactRequestListType,
        page_number=Int(),
        limit=Int(),
        contact_uuid=String(),
        request_title=String(),
        request_detail=String(),
    )

    corporation_profile = Field(
        CorporationProfileType,
        required=True,
        corporation_type=String(required=True),
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
    )

    corporation_place = Field(
        CorporationPlaceType,
        required=True,
        region=String(required=True),
        corporation_uuid=String(required=True),
    )

    corporation_place_list = Field(
        CorporationPlaceListType,
        page_number=Int(),
        limit=Int(),
        region=String(),
        place_uuid=String(),
        corporation_types=List(String),
    )

    company_corporation_profile = Field(
        CompanyCorporationProfileType,
        required=True,
        corporation_uuid=String(required=True),
    )

    company_corporation_profile_list = Field(
        CompanyCorporationProfileListType,
        page_number=Int(),
        limit=Int(),
        external_id=String(),
        corporation_types=List(String),
    )

    contact_chatbot_history = Field(
        ContactChatbotHistoryType,
        required=True,
        timestamp=Int(required=True),
    )

    contact_chatbot_history_list = Field(
        ContactChatbotHistoryListType,
        page_number=Int(),
        limit=Int(),
        contact_uuid=String(),
        place_uuids=List(String),
        regions=List(String),
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
        regions=List(String),
        keyword=String(),
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

    def resolve_question(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> QuestionType:
        return resolve_question(info, **kwargs)

    def resolve_question_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> QuestionListType:
        return resolve_question_list(info, **kwargs)

    def resolve_question_criteria(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> QuestionCriteriaType:
        return resolve_question_criteria(info, **kwargs)

    def resolve_question_criteria_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> QuestionCriteriaListType:
        return resolve_question_criteria_list(info, **kwargs)

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

    def resolve_company_contact_profile(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CompanyContactProfileType:
        return resolve_company_contact_profile(info, **kwargs)

    def resolve_company_contact_profile_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CompanyContactProfileListType:
        return resolve_company_contact_profile_list(info, **kwargs)

    def resolve_company_contact_request(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CompanyContactRequestType:
        return resolve_company_contact_request(info, **kwargs)

    def resolve_company_contact_request_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CompanyContactRequestListType:
        return resolve_company_contact_request_list(info, **kwargs)

    def resolve_corporation_profile(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CorporationProfileType:
        return resolve_corporation_profile(info, **kwargs)

    def resolve_corporation_profile_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CorporationProfileListType:
        return resolve_corporation_profile_list(info, **kwargs)

    def resolve_corporation_place(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CorporationPlaceType:
        return resolve_corporation_place(info, **kwargs)

    def resolve_corporation_place_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CorporationPlaceListType:
        return resolve_corporation_place_list(info, **kwargs)

    def resolve_company_corporation_profile(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CompanyCorporationProfileType:
        return resolve_company_corporation_profile(info, **kwargs)

    def resolve_company_corporation_profile_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CompanyCorporationProfileListType:
        return resolve_company_corporation_profile_list(info, **kwargs)

    def resolve_contact_chatbot_history(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> ContactChatbotHistoryType:
        return resolve_contact_chatbot_history(info, **kwargs)

    def resolve_contact_chatbot_history_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> ContactChatbotHistoryListType:
        return resolve_contact_chatbot_history_list(info, **kwargs)

    def resolve_utm_tag_data_collection(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> UtmTagDataCollectionType:
        return resolve_utm_tag_data_collection(info, **kwargs)

    def resolve_utm_tag_data_collection_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> UtmTagDataCollectionListType:
        return resolve_utm_tag_data_collection_list(info, **kwargs)


class Mutations(ObjectType):
    insert_activity_history = InsertActivityHistory.Field()
    delete_activity_history = DeleteActivityHistory.Field()
    insert_update_question = InsertUpdateQuestion.Field()
    delete_question = DeleteQuestion.Field()
    insert_update_question_criteria = InsertUpdateQuestionCriteria.Field()
    delete_question_criteria = DeleteQuestionCriteria.Field()
    insert_update_place = InsertUpdatePlace.Field()
    delete_place = DeletePlace.Field()
    insert_update_contact_profile = InsertUpdateContactProfile.Field()
    delete_contact_profile = DeleteContactProfile.Field()
    insert_update_company_contact_profile = InsertUpdateCompanyContactProfile.Field()
    delete_company_contact_profile = DeleteCompanyContactProfile.Field()
    insert_update_company_contact_request = InsertUpdateCompanyContactRequest.Field()
    delete_company_contact_request = DeleteCompanyContactRequest.Field()
    insert_update_corporation_profile = InsertUpdateCorporationProfile.Field()
    delete_corporation_profile = DeleteCorporationProfile.Field()
    insert_update_corporation_place = InsertUpdateCorporationPlace.Field()
    delete_corporation_place = DeleteCorporationPlace.Field()
    insert_update_company_corporation_profile = (
        InsertUpdateCompanyCorporationProfile.Field()
    )
    delete_company_corporation_profile = DeleteCompanyCorporationProfile.Field()
    insert_contact_chatbot_history = InsertContactChatbotHistory.Field()
    delete_contact_chatbot_history = DeleteContactChatbotHistory.Field()
    insert_utm_tag_data_collection = InsertUtmTagDataCollection.Field()
    delete_utm_tag_data_collection = DeleteUtmTagDataCollection.Field()
