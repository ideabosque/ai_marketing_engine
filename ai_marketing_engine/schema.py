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
    DeleteCompanyCorporationProfiles,
    DeleteCompanyCustomerProfiles,
    DeleteCorporationPlace,
    DeleteCorporationProfile,
    DeleteCustomerChatbotHistory,
    DeleteCustomerProfile,
    DeletePlace,
    DeleteQuestion,
    DeleteQuestionCriteria,
    DeleteUtmTagDataCollection,
    InsertCustomerChatbotHistory,
    InsertUpdateCompanyCorporationProfiles,
    InsertUpdateCompanyCustomerProfiles,
    InsertUpdateCorporationPlace,
    InsertUpdateCorporationProfile,
    InsertUpdateCustomerProfile,
    InsertUpdatePlace,
    InsertUpdateQuestion,
    InsertUpdateQuestionCriteria,
    InsertUtmTagDataCollection,
)
from .queries import (
    resolve_company_corporation_profiles,
    resolve_company_corporation_profiles_list,
    resolve_company_customer_profiles,
    resolve_company_customer_profiles_list,
    resolve_corporation_place,
    resolve_corporation_place_list,
    resolve_corporation_profile,
    resolve_corporation_profile_list,
    resolve_customer_chatbot_history,
    resolve_customer_chatbot_history_list,
    resolve_customer_profile,
    resolve_customer_profile_list,
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
    CompanyCorporationProfilesListType,
    CompanyCorporationProfilesType,
    CompanyCustomerProfilesListType,
    CompanyCustomerProfilesType,
    CorporationPlaceListType,
    CorporationPlaceType,
    CorporationProfileListType,
    CorporationProfileType,
    CustomerChatbotHistoryListType,
    CustomerChatbotHistoryType,
    CustomerProfileListType,
    CustomerProfileType,
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
        CompanyCorporationProfilesListType,
        CompanyCorporationProfilesType,
        CorporationProfileListType,
        CorporationProfileType,
        CustomerChatbotHistoryListType,
        CustomerChatbotHistoryType,
        CompanyCustomerProfilesListType,
        CompanyCustomerProfilesType,
        CustomerProfileListType,
        CustomerProfileType,
        PlaceListType,
        PlaceType,
        QuestionListType,
        QuestionType,
        UtmTagDataCollectionListType,
        UtmTagDataCollectionType,
    ]


class Query(ObjectType):
    ping = String()
    question = Field(
        QuestionType,
        required=True,
        company_id=String(required=True),
        question_uuid=String(required=True),
    )

    question_list = Field(
        QuestionListType,
        page_number=Int(),
        limit=Int(),
        company_id=String(),
        question_groups=List(String),
        question=String(),
        attribute=String(),
    )

    question_criteria = Field(
        QuestionCriteriaType,
        required=True,
        company_id=String(required=True),
        question_group=String(required=True),
    )

    question_criteria_list = Field(
        QuestionCriteriaListType,
        page_number=Int(),
        limit=Int(),
        company_id=String(),
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

    customer_profile = Field(
        CustomerProfileType,
        required=True,
        place_uuid=String(required=True),
        customer_uuid=String(required=True),
    )

    customer_profile_list = Field(
        CustomerProfileListType,
        page_number=Int(),
        limit=Int(),
        place_uuid=String(),
        email=String(),
        regions=List(String),
        first_name=String(),
        last_name=String(),
    )

    company_customer_profiles = Field(
        CompanyCustomerProfilesType,
        required=True,
        company_id=String(required=True),
        customer_uuid=String(required=True),
    )

    company_customer_profiles_list = Field(
        CompanyCustomerProfilesListType,
        page_number=Int(),
        limit=Int(),
        company_id=String(),
        email=String(),
        corporation_types=List(String),
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

    company_corporation_profiles = Field(
        CompanyCorporationProfilesType,
        required=True,
        company_id=String(required=True),
        corporation_uuid=String(required=True),
    )

    company_corporation_profiles_list = Field(
        CompanyCorporationProfilesListType,
        page_number=Int(),
        limit=Int(),
        company_id=String(),
        external_id=String(),
        corporation_types=List(String),
    )

    customer_chatbot_history = Field(
        CustomerChatbotHistoryType,
        required=True,
        company_id=String(required=True),
        timestamp=Int(required=True),
    )

    customer_chatbot_history_list = Field(
        CustomerChatbotHistoryListType,
        page_number=Int(),
        limit=Int(),
        company_id=String(),
        customer_uuid=String(),
        place_uuids=List(String),
        regions=List(String),
        assistant_types=List(String),
    )

    utm_tag_data_collection = Field(
        UtmTagDataCollectionType,
        required=True,
        company_id=String(required=True),
        collection_uuid=String(required=True),
    )

    utm_tag_data_collection_list = Field(
        UtmTagDataCollectionListType,
        page_number=Int(),
        limit=Int(),
        company_id=String(),
        tag_name=String(),
        place_uuids=List(String),
        customer_uuids=List(String),
        regions=List(String),
        keyword=String(),
    )

    def resolve_ping(self, info: ResolveInfo) -> str:
        return f"Hello at {time.strftime('%X')}!!"

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

    def resolve_customer_profile(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CustomerProfileType:
        return resolve_customer_profile(info, **kwargs)

    def resolve_customer_profile_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CustomerProfileListType:
        return resolve_customer_profile_list(info, **kwargs)

    def resolve_company_customer_profiles(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CompanyCustomerProfilesType:
        return resolve_company_customer_profiles(info, **kwargs)

    def resolve_company_customer_profiles_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CompanyCustomerProfilesListType:
        return resolve_company_customer_profiles_list(info, **kwargs)

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

    def resolve_company_corporation_profiles(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CompanyCorporationProfilesType:
        return resolve_company_corporation_profiles(info, **kwargs)

    def resolve_company_corporation_profiles_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CompanyCorporationProfilesListType:
        return resolve_company_corporation_profiles_list(info, **kwargs)

    def resolve_customer_chatbot_history(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CustomerChatbotHistoryType:
        return resolve_customer_chatbot_history(info, **kwargs)

    def resolve_customer_chatbot_history_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> CustomerChatbotHistoryListType:
        return resolve_customer_chatbot_history_list(info, **kwargs)

    def resolve_utm_tag_data_collection(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> UtmTagDataCollectionType:
        return resolve_utm_tag_data_collection(info, **kwargs)

    def resolve_utm_tag_data_collection_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> UtmTagDataCollectionListType:
        return resolve_utm_tag_data_collection_list(info, **kwargs)


class Mutations(ObjectType):
    insert_update_question = InsertUpdateQuestion.Field()
    delete_question = DeleteQuestion.Field()
    insert_update_question_criteria = InsertUpdateQuestionCriteria.Field()
    delete_question_criteria = DeleteQuestionCriteria.Field()
    insert_update_place = InsertUpdatePlace.Field()
    delete_place = DeletePlace.Field()
    insert_update_customer_profile = InsertUpdateCustomerProfile.Field()
    delete_customer_profile = DeleteCustomerProfile.Field()
    insert_update_company_customer_profiles = (
        InsertUpdateCompanyCustomerProfiles.Field()
    )
    delete_company_customer_profiles = DeleteCompanyCustomerProfiles.Field()
    insert_update_corporation_profile = InsertUpdateCorporationProfile.Field()
    delete_corporation_profile = DeleteCorporationProfile.Field()
    insert_update_corporation_place = InsertUpdateCorporationPlace.Field()
    delete_corporation_place = DeleteCorporationPlace.Field()
    insert_update_company_corporation_profiles = (
        InsertUpdateCompanyCorporationProfiles.Field()
    )
    delete_company_corporation_profiles = DeleteCompanyCorporationProfiles.Field()
    insert_customer_chatbot_history = InsertCustomerChatbotHistory.Field()
    delete_customer_chatbot_history = DeleteCustomerChatbotHistory.Field()
    insert_utm_tag_data_collection = InsertUtmTagDataCollection.Field()
    delete_utm_tag_data_collection = DeleteUtmTagDataCollection.Field()
