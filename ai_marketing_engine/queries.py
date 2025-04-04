#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from .handlers import (
    resolve_activity_history_handler,
    resolve_activity_history_list_handler,
    resolve_company_contact_profile_handler,
    resolve_company_contact_profile_list_handler,
    resolve_company_contact_request_handler,
    resolve_company_contact_request_list_handler,
    resolve_company_corporation_profile_handler,
    resolve_company_corporation_profile_list_handler,
    resolve_contact_profile_handler,
    resolve_contact_profile_list_handler,
    resolve_corporation_place_handler,
    resolve_corporation_place_list_handler,
    resolve_corporation_profile_handler,
    resolve_corporation_profile_list_handler,
    resolve_crm_user_list_handler,
    resolve_place_handler,
    resolve_place_list_handler,
    resolve_presigned_upload_url_handler,
    resolve_question_criteria_handler,
    resolve_question_criteria_list_handler,
    resolve_question_handler,
    resolve_question_list_handler,
    resolve_utm_tag_data_collection_handler,
    resolve_utm_tag_data_collection_list_handler,
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
    ContactProfileListType,
    ContactProfileType,
    CorporationPlaceListType,
    CorporationPlaceType,
    CorporationProfileListType,
    CorporationProfileType,
    CrmUserListType,
    PlaceListType,
    PlaceType,
    PresignedUploadUrlType,
    QuestionCriteriaListType,
    QuestionCriteriaType,
    QuestionListType,
    QuestionType,
    UtmTagDataCollectionListType,
    UtmTagDataCollectionType,
)


def resolve_presigned_upload_url(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> PresignedUploadUrlType:
    return resolve_presigned_upload_url_handler(info, **kwargs)


def resolve_activity_history(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ActivityHistoryType:
    return resolve_activity_history_handler(info, **kwargs)


def resolve_activity_history_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ActivityHistoryListType:
    return resolve_activity_history_list_handler(info, **kwargs)


def resolve_question(info: ResolveInfo, **kwargs: Dict[str, Any]) -> QuestionType:
    return resolve_question_handler(info, **kwargs)


def resolve_question_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> QuestionListType:
    return resolve_question_list_handler(info, **kwargs)


def resolve_question_criteria(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> QuestionCriteriaType:
    return resolve_question_criteria_handler(info, **kwargs)


def resolve_question_criteria_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> QuestionCriteriaListType:
    return resolve_question_criteria_list_handler(info, **kwargs)


def resolve_place(info: ResolveInfo, **kwargs: Dict[str, Any]) -> PlaceType:
    return resolve_place_handler(info, **kwargs)


def resolve_place_list(info: ResolveInfo, **kwargs: Dict[str, Any]) -> PlaceListType:
    return resolve_place_list_handler(info, **kwargs)


def resolve_contact_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactProfileType:
    return resolve_contact_profile_handler(info, **kwargs)


def resolve_contact_profile_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactProfileListType:
    return resolve_contact_profile_list_handler(info, **kwargs)


def resolve_company_contact_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CompanyContactProfileType:
    return resolve_company_contact_profile_handler(info, **kwargs)


def resolve_company_contact_profile_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CompanyContactProfileListType:
    return resolve_company_contact_profile_list_handler(info, **kwargs)


def resolve_company_contact_request(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CompanyContactRequestType:
    return resolve_company_contact_request_handler(info, **kwargs)


def resolve_company_contact_request_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CompanyContactRequestListType:
    return resolve_company_contact_request_list_handler(info, **kwargs)


def resolve_corporation_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CorporationProfileType:
    return resolve_corporation_profile_handler(info, **kwargs)


def resolve_corporation_profile_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CorporationProfileListType:
    return resolve_corporation_profile_list_handler(info, **kwargs)


def resolve_company_corporation_profile(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CompanyCorporationProfileType:
    return resolve_company_corporation_profile_handler(info, **kwargs)


def resolve_company_corporation_profile_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CompanyCorporationProfileListType:
    return resolve_company_corporation_profile_list_handler(info, **kwargs)


def resolve_corporation_place(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CorporationPlaceType:
    return resolve_corporation_place_handler(info, **kwargs)


def resolve_corporation_place_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CorporationPlaceListType:
    return resolve_corporation_place_list_handler(info, **kwargs)


def resolve_utm_tag_data_collection(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> UtmTagDataCollectionType:
    return resolve_utm_tag_data_collection_handler(info, **kwargs)


def resolve_utm_tag_data_collection_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> UtmTagDataCollectionListType:
    return resolve_utm_tag_data_collection_list_handler(info, **kwargs)


def resolve_crm_user_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CrmUserListType:
    return resolve_crm_user_list_handler(info, **kwargs)
