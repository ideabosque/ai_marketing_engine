#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from pynamodb.attributes import (
    BooleanAttribute,
    ListAttribute,
    MapAttribute,
    NumberAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.indexes import AllProjection, LocalSecondaryIndex

from silvaengine_dynamodb_base import BaseModel


class QuestionGroupIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "question_group-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    company_id = UnicodeAttribute(hash_key=True)
    question_group = UnicodeAttribute(range_key=True)


class QuestionModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-questions"

    company_id = UnicodeAttribute(hash_key=True)
    question_uuid = UnicodeAttribute(range_key=True)
    question_group = UnicodeAttribute()
    question = UnicodeAttribute()
    priority = NumberAttribute()
    attribute = UnicodeAttribute()
    option_values = ListAttribute(of=UnicodeAttribute, null=True)
    condition = ListAttribute(of=MapAttribute, null=True)
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    question_group_index = QuestionGroupIndex()


class QuestionCriteriaModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-question_criterias"

    company_id = UnicodeAttribute(hash_key=True)
    question_group = UnicodeAttribute(range_key=True)
    region = UnicodeAttribute()
    question_criteria = MapAttribute(default={})
    weight = NumberAttribute(default=0)
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()


class PlaceModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-places"

    region = UnicodeAttribute(hash_key=True)
    place_uuid = UnicodeAttribute(range_key=True)
    latitude = UnicodeAttribute()
    longitude = UnicodeAttribute()
    business_name = UnicodeAttribute()
    address = UnicodeAttribute()
    phone_number = UnicodeAttribute(null=True)
    website = UnicodeAttribute(null=True)
    types = ListAttribute(of=UnicodeAttribute, null=True)
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()


class EmailIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "email-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    place_uuid = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute(range_key=True)


class ContactProfileModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-contact_profiles"

    place_uuid = UnicodeAttribute(hash_key=True)
    contact_uuid = UnicodeAttribute(range_key=True)
    email = UnicodeAttribute()
    region = UnicodeAttribute()
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)
    corporation_type = UnicodeAttribute(null=True)
    corporation_uuid = UnicodeAttribute(null=True)
    data = MapAttribute(null=True)
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    email_index = EmailIndex()


class CompanyEmailIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "email-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    company_id = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute(range_key=True)


class CompanyContactProfileModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-company_contact_profiles"

    company_id = UnicodeAttribute(hash_key=True)
    contact_uuid = UnicodeAttribute(range_key=True)
    email = UnicodeAttribute()
    place_uuid = UnicodeAttribute()
    data = MapAttribute(null=True)
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    email_index = CompanyEmailIndex()


class CompanyContactRequestModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-company_contact_requests"

    contact_uuid = UnicodeAttribute(hash_key=True)
    request_uuid = UnicodeAttribute(range_key=True)
    company_id = UnicodeAttribute()
    request_title = UnicodeAttribute()
    request_detail = UnicodeAttribute()
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()


class ExternalIdIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "external_id-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    corporation_type = UnicodeAttribute(hash_key=True)
    external_id = UnicodeAttribute(range_key=True)


class CorporationProfileModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-corporation_profiles"

    corporation_type = UnicodeAttribute(hash_key=True)
    corporation_uuid = UnicodeAttribute(range_key=True)
    external_id = UnicodeAttribute()
    business_name = UnicodeAttribute()
    categories = ListAttribute(of=UnicodeAttribute, null=True)
    address = MapAttribute()
    data = MapAttribute(null=True)
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    external_id_index = ExternalIdIndex()


class PlaceUuidIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "place_uuid-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    region = UnicodeAttribute(hash_key=True)
    place_uuid = UnicodeAttribute(range_key=True)


class CorporationPlaceModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-corporation_places"

    region = UnicodeAttribute(hash_key=True)
    corporation_uuid = UnicodeAttribute(range_key=True)
    place_uuid = UnicodeAttribute()
    corporation_type = UnicodeAttribute()
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    place_uuid_index = PlaceUuidIndex()


class CompanyExternalIdIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "external_id-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    company_id = UnicodeAttribute(hash_key=True)
    external_id = UnicodeAttribute(range_key=True)


class CompanyCorporationProfileModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-company_corporation_profiles"

    company_id = UnicodeAttribute(hash_key=True)
    corporation_uuid = UnicodeAttribute(range_key=True)
    external_id = UnicodeAttribute()
    corporation_type = UnicodeAttribute()
    data = MapAttribute(null=True)
    updated_by = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    external_id_index = CompanyExternalIdIndex()


class ContactUuidIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "contact_uuid-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    company_id = UnicodeAttribute(hash_key=True)
    contact_uuid = UnicodeAttribute(range_key=True)


class ContactChatbotHistoryModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-contact_chatbot_history"

    company_id = UnicodeAttribute(hash_key=True)
    timestamp = NumberAttribute(range_key=True)
    contact_uuid = UnicodeAttribute()
    place_uuid = UnicodeAttribute()
    region = UnicodeAttribute()
    assistant_id = UnicodeAttribute()
    thread_id = UnicodeAttribute()
    endpoint_id = UnicodeAttribute()
    contact_uuid_index = ContactUuidIndex()


class TageNameIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "tag_naame-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    company_id = UnicodeAttribute(hash_key=True)
    tag_name = UnicodeAttribute(range_key=True)


class UtmTagDataCollectionModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "ame-utm_tag_data_collection"

    company_id = UnicodeAttribute(hash_key=True)
    collection_uuid = UnicodeAttribute(range_key=True)
    tag_name = UnicodeAttribute()
    place_uuid = UnicodeAttribute()
    contact_uuid = UnicodeAttribute()
    region = UnicodeAttribute()
    keyword = UnicodeAttribute()
    utm_campaign = UnicodeAttribute()
    utm_content = UnicodeAttribute()
    utm_medium = UnicodeAttribute()
    utm_source = UnicodeAttribute()
    utm_term = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    tag_name_index = TageNameIndex()
