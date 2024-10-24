#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import traceback
from typing import Any, Dict

from graphene import Boolean, DateTime, Field, Float, Int, List, Mutation, String
from silvaengine_utility import JSON

from .handlers import (
    delete_company_corporation_profile_handler,
    delete_company_customer_profile_handler,
    delete_corporation_place_handler,
    delete_corporation_profile_handler,
    delete_customer_chatbot_history_handler,
    delete_customer_profile_handler,
    delete_place_handler,
    delete_question_criteria_handler,
    delete_question_handler,
    delete_utm_tag_data_collection_handler,
    insert_customer_chatbot_history_handler,
    insert_update_company_corporation_profile_handler,
    insert_update_company_customer_profile_handler,
    insert_update_corporation_place_handler,
    insert_update_corporation_profile_handler,
    insert_update_customer_profile_handler,
    insert_update_place_handler,
    insert_update_question_criteria_handler,
    insert_update_question_handler,
    insert_utm_tag_data_collection_handler,
)
from .types import (
    CompanyCorporationProfileType,
    CompanyCustomerProfileType,
    CorporationPlaceType,
    CorporationProfileType,
    CustomerChatbotHistoryType,
    CustomerProfileType,
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


class InsertUpdateCustomerProfile(Mutation):
    customer_profile = Field(CustomerProfileType)

    class Arguments:
        place_uuid = String(required=True)
        customer_uuid = String(required=False)
        email = String(required=False)
        region = String(required=False)
        first_name = String(required=False)
        last_name = String(required=False)
        data = JSON(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateCustomerProfile":
        try:
            customer_profile = insert_update_customer_profile_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateCustomerProfile(customer_profile=customer_profile)


class DeleteCustomerProfile(Mutation):
    ok = Boolean()

    class Arguments:
        place_uuid = String(required=True)
        customer_uuid = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteCustomerProfile":
        try:
            ok = delete_customer_profile_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteCustomerProfile(ok=ok)


class InsertUpdateCompanyCustomerProfile(Mutation):
    company_customer_profile = Field(CompanyCustomerProfileType)

    class Arguments:
        company_id = String(required=True)
        customer_uuid = String(required=True)
        email = String(required=False)
        place_uuid = String(required=False)
        corporation_type = String(required=False)
        corporation_uuid = String(required=False)
        data = JSON(required=False)
        updated_by = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertUpdateCompanyCustomerProfile":
        try:
            company_customer_profile = insert_update_company_customer_profile_handler(
                info, **kwargs
            )
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertUpdateCompanyCustomerProfile(
            company_customer_profile=company_customer_profile
        )


class DeleteCompanyCustomerProfile(Mutation):
    ok = Boolean()

    class Arguments:
        company_id = String(required=True)
        customer_uuid = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteCompanyCustomerProfile":
        try:
            ok = delete_company_customer_profile_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteCompanyCustomerProfile(ok=ok)


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


class InsertCustomerChatbotHistory(Mutation):
    customer_chatbot_history = Field(CustomerChatbotHistoryType)

    class Arguments:
        company_id = String(required=True)
        timestamp = Int(required=True)
        customer_uuid = String(required=True)
        place_uuid = String(required=True)
        region = String(required=True)
        assistant_id = String(required=True)
        thread_id = String(required=True)
        assistant_type = String(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "InsertCustomerChatbotHistory":
        try:
            customer_chatbot_history = insert_customer_chatbot_history_handler(
                info, **kwargs
            )
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return InsertCustomerChatbotHistory(
            customer_chatbot_history=customer_chatbot_history
        )


class DeleteCustomerChatbotHistory(Mutation):
    ok = Boolean()

    class Arguments:
        company_id = String(required=True)
        timestamp = Int(required=True)

    @staticmethod
    def mutate(
        root: Any, info: Any, **kwargs: Dict[str, Any]
    ) -> "DeleteCustomerChatbotHistory":
        try:
            ok = delete_customer_chatbot_history_handler(info, **kwargs)
        except Exception as e:
            log = traceback.format_exc()
            info.context.get("logger").error(log)
            raise e

        return DeleteCustomerChatbotHistory(ok=ok)


class InsertUtmTagDataCollection(Mutation):
    utm_tag_data_collection = Field(UtmTagDataCollectionType)

    class Arguments:
        company_id = String(required=True)
        tag_name = String(required=True)
        place_uuid = String(required=True)
        customer_uuid = String(required=True)
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
