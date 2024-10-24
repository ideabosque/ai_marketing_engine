#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from .handlers import (
    resolve_company_corporation_profile_handler,
    resolve_company_corporation_profile_list_handler,
    resolve_company_customer_profile_handler,
    resolve_company_customer_profile_list_handler,
    resolve_corporation_place_handler,
    resolve_corporation_place_list_handler,
    resolve_corporation_profile_handler,
    resolve_corporation_profile_list_handler,
    resolve_customer_chatbot_history_handler,
    resolve_customer_chatbot_history_list_handler,
    resolve_customer_profile_handler,
    resolve_customer_profile_list_handler,
    resolve_place_handler,
    resolve_place_list_handler,
    resolve_question_criteria_handler,
    resolve_question_criteria_list_handler,
    resolve_question_handler,
    resolve_question_list_handler,
    resolve_utm_tag_data_collection_handler,
    resolve_utm_tag_data_collection_list_handler,
)


def resolve_question(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_question_handler(info, **kwargs)


def resolve_question_list(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_question_list_handler(info, **kwargs)


def resolve_question_criteria(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_question_criteria_handler(info, **kwargs)


def resolve_question_criteria_list(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_question_criteria_list_handler(info, **kwargs)


def resolve_place(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_place_handler(info, **kwargs)


def resolve_place_list(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_place_list_handler(info, **kwargs)


def resolve_customer_profile(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_customer_profile_handler(info, **kwargs)


def resolve_customer_profile_list(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_customer_profile_list_handler(info, **kwargs)


def resolve_company_customer_profile(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_company_customer_profile_handler(info, **kwargs)


def resolve_company_customer_profile_list(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_company_customer_profile_list_handler(info, **kwargs)


def resolve_corporation_profile(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_corporation_profile_handler(info, **kwargs)


def resolve_corporation_profile_list(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_corporation_profile_list_handler(info, **kwargs)


def resolve_company_corporation_profile(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_company_corporation_profile_handler(info, **kwargs)


def resolve_company_corporation_profile_list(
    info: ResolveInfo, **kwargs: Dict[Any, Any]
):
    return resolve_company_corporation_profile_list_handler(info, **kwargs)


def resolve_corporation_place(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_corporation_place_handler(info, **kwargs)


def resolve_corporation_place_list(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_corporation_place_list_handler(info, **kwargs)


def resolve_customer_chatbot_history(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_customer_chatbot_history_handler(info, **kwargs)


def resolve_customer_chatbot_history_list(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_customer_chatbot_history_list_handler(info, **kwargs)


def resolve_utm_tag_data_collection(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_utm_tag_data_collection_handler(info, **kwargs)


def resolve_utm_tag_data_collection_list(info: ResolveInfo, **kwargs: Dict[Any, Any]):
    return resolve_utm_tag_data_collection_list_handler(info, **kwargs)
