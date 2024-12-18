#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from .handlers import (
    resolve_company_contact_profile_handler,
    resolve_company_contact_profile_list_handler,
    resolve_company_corporation_profile_handler,
    resolve_company_corporation_profile_list_handler,
    resolve_contact_chatbot_history_handler,
    resolve_contact_chatbot_history_list_handler,
    resolve_contact_profile_handler,
    resolve_contact_profile_list_handler,
    resolve_contact_request_handler,
    resolve_contact_request_list_handler,
    resolve_corporation_place_handler,
    resolve_corporation_place_list_handler,
    resolve_corporation_profile_handler,
    resolve_corporation_profile_list_handler,
    resolve_place_handler,
    resolve_place_list_handler,
    resolve_question_criteria_handler,
    resolve_question_criteria_list_handler,
    resolve_question_handler,
    resolve_question_list_handler,
    resolve_utm_tag_data_collection_handler,
    resolve_utm_tag_data_collection_list_handler,
)
from .types import (
    CompanyContactProfileListType,
    CompanyContactProfileType,
    CompanyCorporationProfileListType,
    CompanyCorporationProfileType,
    ContactChatbotHistoryListType,
    ContactChatbotHistoryType,
    ContactProfileListType,
    ContactProfileType,
    ContactRequestListType,
    ContactRequestType,
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


def resolve_question(info: ResolveInfo, **kwargs: Dict[Any, Any]) -> QuestionType:
    return resolve_question_handler(info, **kwargs)


def resolve_question_list(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> QuestionListType:
    return resolve_question_list_handler(info, **kwargs)


def resolve_question_criteria(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> QuestionCriteriaType:
    return resolve_question_criteria_handler(info, **kwargs)


def resolve_question_criteria_list(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> QuestionCriteriaListType:
    return resolve_question_criteria_list_handler(info, **kwargs)


def resolve_place(info: ResolveInfo, **kwargs: Dict[Any, Any]) -> PlaceType:
    return resolve_place_handler(info, **kwargs)


def resolve_place_list(info: ResolveInfo, **kwargs: Dict[Any, Any]) -> PlaceListType:
    return resolve_place_list_handler(info, **kwargs)


def resolve_contact_profile(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> ContactProfileType:
    return resolve_contact_profile_handler(info, **kwargs)


def resolve_contact_profile_list(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> ContactProfileListType:
    return resolve_contact_profile_list_handler(info, **kwargs)


def resolve_company_contact_profile(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> CompanyContactProfileType:
    return resolve_company_contact_profile_handler(info, **kwargs)


def resolve_company_contact_profile_list(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> CompanyContactProfileListType:
    return resolve_company_contact_profile_list_handler(info, **kwargs)


def resolve_contact_request(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> ContactRequestType:
    return resolve_contact_request_handler(info, **kwargs)


def resolve_contact_request_list(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> ContactRequestListType:
    return resolve_contact_request_list_handler(info, **kwargs)


def resolve_corporation_profile(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> CorporationProfileType:
    return resolve_corporation_profile_handler(info, **kwargs)


def resolve_corporation_profile_list(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> CorporationProfileListType:
    return resolve_corporation_profile_list_handler(info, **kwargs)


def resolve_company_corporation_profile(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> CompanyCorporationProfileType:
    return resolve_company_corporation_profile_handler(info, **kwargs)


def resolve_company_corporation_profile_list(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> CompanyCorporationProfileListType:
    return resolve_company_corporation_profile_list_handler(info, **kwargs)


def resolve_corporation_place(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> CorporationPlaceType:
    return resolve_corporation_place_handler(info, **kwargs)


def resolve_corporation_place_list(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> CorporationPlaceListType:
    return resolve_corporation_place_list_handler(info, **kwargs)


def resolve_contact_chatbot_history(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> ContactChatbotHistoryType:
    return resolve_contact_chatbot_history_handler(info, **kwargs)


def resolve_contact_chatbot_history_list(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> ContactChatbotHistoryListType:
    return resolve_contact_chatbot_history_list_handler(info, **kwargs)


def resolve_utm_tag_data_collection(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> UtmTagDataCollectionType:
    return resolve_utm_tag_data_collection_handler(info, **kwargs)


def resolve_utm_tag_data_collection_list(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
) -> UtmTagDataCollectionListType:
    return resolve_utm_tag_data_collection_list_handler(info, **kwargs)
