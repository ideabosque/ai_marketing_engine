#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import traceback
from typing import Any, Dict

from graphene import Boolean, DateTime, Field, Float, Int, List, Mutation, String
from silvaengine_utility import JSON

from .handlers import (
    delete_company_contact_profile_handler,
    delete_company_corporation_profile_handler,
    delete_contact_chatbot_history_handler,
    delete_contact_profile_handler,
    delete_corporation_place_handler,
    delete_corporation_profile_handler,
    delete_place_handler,
    delete_question_criteria_handler,
    delete_question_handler,
    delete_utm_tag_data_collection_handler,
    insert_contact_chatbot_history_handler,
    insert_update_company_contact_profile_handler,
    insert_update_company_corporation_profile_handler,
    insert_update_contact_profile_handler,
    insert_update_corporation_place_handler,
    insert_update_corporation_profile_handler,
    insert_update_place_handler,
    insert_update_question_criteria_handler,
    insert_update_question_handler,
    insert_utm_tag_data_collection_handler,
)
from .types import (
    CompanyContactProfileType,
    CompanyCorporationProfileType,
    ContactChatbotHistoryType,
    ContactProfileType,
    CorporationPlaceType,
    CorporationProfileType,
    PlaceType,
    QuestionCriteriaType,
    QuestionType,
    UtmTagDataCollectionType,
)


class InsertUpdateQuestion(Mutation):
    question = Field(QuestionType)

    class Arguments:
        company_id = String(required=True)
        question_uuid = String(required=False)
        question_group = String(required=False)
        question = String(required=False)
        priority = Int(required=False)
        attribute = String(required=False)
        option_values = List(String, required=False)
        condition = List(JSON, required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateQuestion":
        try:
            question = insert_update_question_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateQuestion(question=question)


class DeleteQuestion(Mutation):
    ok = Boolean()

    class Arguments:
        company_id = String(required=True)
        question_uuid = String(required=True)

    @staticmethod
    def mutate(root: Any, info: Any, **kwargs: Dict[str, Any]) -> "DeleteQuestion":
        try:
            ok = delete_question_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteQuestion(ok=ok)


class InsertUpdateQuestionCriteria(Mutation):
    question_criteria = Field(QuestionCriteriaType)

    class Arguments:
        company_id = String(required=True)
        question_group = String(required=True)
        region = String(required=True)
        question_criteria = JSON(required=False)
        weight = Int(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateQuestionCriteria":
        try:
            question_criteria = insert_update_question_criteria_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateQuestionCriteria(question_criteria=question_criteria)


class DeleteQuestionCriteria(Mutation):
    ok = Boolean()

    class Arguments:
        company_id = String(required=True)
        question_group = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteQuestionCriteria":
        try:
            ok = delete_question_criteria_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteQuestionCriteria(ok=ok)


class InsertUpdatePlace(Mutation):
    place = Field(PlaceType)

    class Arguments:
        region = String(required=True)
        place_uuid = String(required=False)
        latitude = String(required=False)
        longitude = String(required=False)
        business_name = String(required=False)
        address = String(required=False)
        phone_number = String(required=False)
        website = String(required=False)
        types = List(String, required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(root: Any, info: Any, **kwargs: Dict[str, Any]) -> "InsertUpdatePlace":
        try:
            place = insert_update_place_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdatePlace(place=place)


class DeletePlace(Mutation):
    ok = Boolean()

    class Arguments:
        region = String(required=True)
        place_uuid = String(required=True)

    @staticmethod
    def mutate(root: Any, info: Any, **kwargs: Dict[str, Any]) -> "DeletePlace":
        try:
            ok = delete_place_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeletePlace(ok=ok)


class InsertUpdateContactProfile(Mutation):
    contact_profile = Field(ContactProfileType)

    class Arguments:
        place_uuid = String(required=True)
        contact_uuid = String(required=False)
        email = String(required=False)
        region = String(required=False)
        first_name = String(required=False)
        last_name = String(required=False)
        corporation_type = String(required=False)
        corporation_uuid = String(required=False)
        data = JSON(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateContactProfile":
        try:
            contact_profile = insert_update_contact_profile_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateContactProfile(contact_profile=contact_profile)


class DeleteContactProfile(Mutation):
    ok = Boolean()

    class Arguments:
        place_uuid = String(required=True)
        contact_uuid = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteContactProfile":
        try:
            ok = delete_contact_profile_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteContactProfile(ok=ok)


class InsertUpdateCompanyContactProfile(Mutation):
    company_contact_profile = Field(CompanyContactProfileType)

    class Arguments:
        company_id = String(required=True)
        contact_uuid = String(required=True)
        email = String(required=False)
        place_uuid = String(required=False)
        data = JSON(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateCompanyContactProfile":
        try:
            company_contact_profile = insert_update_company_contact_profile_handler(
                info, **kwargs
            )
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateCompanyContactProfile(
            company_contact_profile=company_contact_profile
        )


class DeleteCompanyContactProfile(Mutation):
    ok = Boolean()

    class Arguments:
        company_id = String(required=True)
        contact_uuid = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteCompanyContactProfile":
        try:
            ok = delete_company_contact_profile_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteCompanyContactProfile(ok=ok)


class InsertUpdateCorporationProfile(Mutation):
    corporation_profile = Field(CorporationProfileType)

    class Arguments:
        corporation_type = String(required=True)
        corporation_uuid = String(required=False)
        external_id = String(required=False)
        business_name = String(required=False)
        categories = List(String, required=False)
        address = JSON(required=False)
        data = JSON(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateCorporationProfile":
        try:
            corporation_profile = insert_update_corporation_profile_handler(
                info, **kwargs
            )
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateCorporationProfile(corporation_profile=corporation_profile)


class DeleteCorporationProfile(Mutation):
    ok = Boolean()

    class Arguments:
        corporation_type = String(required=True)
        corporation_uuid = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteCorporationProfile":
        try:
            ok = delete_corporation_profile_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteCorporationProfile(ok=ok)


class InsertUpdateCorporationPlace(Mutation):
    corporation_place = Field(CorporationPlaceType)

    class Arguments:
        region = String(required=True)
        corporation_uuid = String(required=True)
        place_uuid = String(required=True)
        corporation_type = String(required=True)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateCorporationPlace":
        try:
            corporation_place = insert_update_corporation_place_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateCorporationPlace(corporation_place=corporation_place)


class DeleteCorporationPlace(Mutation):
    ok = Boolean()

    class Arguments:
        region = String(required=True)
        corporation_uuid = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteCorporationPlace":
        try:
            ok = delete_corporation_place_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteCorporationPlace(ok=ok)


class InsertUpdateCompanyCorporationProfile(Mutation):
    company_corporation_profile = Field(CompanyCorporationProfileType)

    class Arguments:
        company_id = String(required=True)
        corporation_uuid = String(required=True)
        external_id = String(required=False)
        corporation_type = String(required=False)
        data = JSON(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateCompanyCorporationProfile":
        try:
            company_corporation_profile = (
                insert_update_company_corporation_profile_handler(info, **kwargs)
            )
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateCompanyCorporationProfile(
            company_corporation_profile=company_corporation_profile
        )


class DeleteCompanyCorporationProfile(Mutation):
    ok = Boolean()

    class Arguments:
        company_id = String(required=True)
        corporation_uuid = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteCompanyCorporationProfile":
        try:
            ok = delete_company_corporation_profile_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteCompanyCorporationProfile(ok=ok)


class InsertContactChatbotHistory(Mutation):
    contact_chatbot_history = Field(ContactChatbotHistoryType)

    class Arguments:
        company_id = String(required=True)
        timestamp = Int(required=True)
        contact_uuid = String(required=True)
        place_uuid = String(required=True)
        region = String(required=True)
        assistant_id = String(required=True)
        thread_id = String(required=True)
        assistant_type = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertContactChatbotHistory":
        try:
            contact_chatbot_history = insert_contact_chatbot_history_handler(
                info, **kwargs
            )
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertContactChatbotHistory(
            contact_chatbot_history=contact_chatbot_history
        )


class DeleteContactChatbotHistory(Mutation):
    ok = Boolean()

    class Arguments:
        company_id = String(required=True)
        timestamp = Int(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteContactChatbotHistory":
        try:
            ok = delete_contact_chatbot_history_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteContactChatbotHistory(ok=ok)


class InsertUtmTagDataCollection(Mutation):
    utm_tag_data_collection = Field(UtmTagDataCollectionType)

    class Arguments:
        company_id = String(required=True)
        tag_name = String(required=True)
        place_uuid = String(required=True)
        contact_uuid = String(required=True)
        region = String(required=True)
        keyword = String(required=True)
        utm_campaign = String(required=True)
        utm_content = String(required=True)
        utm_medium = String(required=True)
        utm_source = String(required=True)
        utm_term = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUtmTagDataCollection":
        try:
            utm_tag_data_collection = insert_utm_tag_data_collection_handler(
                info, **kwargs
            )
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUtmTagDataCollection(
            utm_tag_data_collection=utm_tag_data_collection
        )


class DeleteUtmTagDataCollection(Mutation):
    ok = Boolean()

    class Arguments:
        company_id = String(required=True)
        collection_uuid = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteUtmTagDataCollection":
        try:
            ok = delete_utm_tag_data_collection_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteUtmTagDataCollection(ok=ok)
