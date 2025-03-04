#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import (
    Boolean,
    DateTime,
    Decimal,
    Field,
    Float,
    Int,
    List,
    ObjectType,
    String,
)

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON


class QuestionType(ObjectType):
    endpoint_id = String()
    question_uuid = String()
    question_group = String()
    question = String()
    priority = Int()
    attribute = String()
    option_values = List(String)
    condition = List(JSON)
    updated_by = String()
    updated_at = DateTime()
    created_at = DateTime()


class QuestionCriteriaType(ObjectType):
    endpoint_id = String()
    question_group = String()
    region = String()
    question_criteria = JSON()
    weight = Int()
    updated_by = String()
    updated_at = DateTime()
    created_at = DateTime()


class PlaceType(ObjectType):
    region = String()
    place_uuid = String()
    latitude = String()
    longitude = String()
    business_name = String()
    address = String()
    phone_number = String()
    website = String()
    types = List(String)
    updated_by = String()
    updated_at = DateTime()
    created_at = DateTime()


class ContactProfileType(ObjectType):
    place = JSON()
    contact_uuid = String()
    email = String()
    first_name = String()
    last_name = String()
    corporation_profile = JSON()
    data = JSON()
    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()


class CompanyContactProfileType(ObjectType):
    endpoint_id = String()
    contact_profile = JSON()
    email = String()
    data = JSON()
    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()


class CompanyContactRequestType(ObjectType):
    company_contact_profile = JSON()
    request_uuid = String()
    request_title = String()
    request_detail = String()
    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()


class CorporationProfileType(ObjectType):
    corporation_type = String()
    corporation_uuid = String()
    external_id = String()
    business_name = String()
    categories = List(String)
    address = String()
    data = JSON()
    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()


class CorporationPlaceType(ObjectType):
    corporation_profile = JSON()
    place = JSON()
    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()


class CompanyCorporationProfileType(ObjectType):
    endpoint_id = String()
    corporation_profile = JSON()
    external_id = String()
    data = JSON()
    updated_by = String()
    created_at = DateTime()
    updated_at = DateTime()


class ContactChatbotHistoryType(ObjectType):
    endpoint_id = String()
    timestamp = Int()
    contact_uuid = String()
    place_uuid = String()
    region = String()
    assistant_id = String()
    thread_id = String()


class UtmTagDataCollectionType(ObjectType):
    endpoint_id = String()
    collection_uuid = String()
    tag_name = String()
    place = JSON()
    contact_profile = JSON()
    keyword = String()
    utm_campaign = String()
    utm_content = String()
    utm_medium = String()
    utm_source = String()
    utm_term = String()
    created_at = DateTime()


class QuestionListType(ListObjectType):
    question_list = List(QuestionType)


class QuestionCriteriaListType(ListObjectType):
    question_criteria_list = List(QuestionCriteriaType)


class PlaceListType(ListObjectType):
    place_list = List(PlaceType)


class ContactProfileListType(ListObjectType):
    contact_profile_list = List(ContactProfileType)


class CompanyContactProfileListType(ListObjectType):
    company_contact_profile_list = List(CompanyContactProfileType)


class CompanyContactRequestListType(ListObjectType):
    company_contact_request_list = List(CompanyContactRequestType)


class CorporationProfileListType(ListObjectType):
    corporation_profile_list = List(CorporationProfileType)


class CorporationPlaceListType(ListObjectType):
    corporation_place_list = List(CorporationPlaceType)


class CompanyCorporationProfileListType(ListObjectType):
    company_corporation_profile_list = List(CompanyCorporationProfileType)


class ContactChatbotHistoryListType(ListObjectType):
    contact_chatbot_history_list = List(ContactChatbotHistoryType)


class UtmTagDataCollectionListType(ListObjectType):
    utm_tag_data_collection_list = List(UtmTagDataCollectionType)
