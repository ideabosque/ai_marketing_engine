#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
from typing import Any, Dict, List
from graphene import Schema
from silvaengine_utility import Graphql
from silvaengine_dynamodb_base import BaseModel
from .handlers.config import Config
from .schema import Mutations, Query, type_class


# Hook function applied to deployment
def deploy() -> List:
    return [
        {
            "service": "AI Assistant",
            "class": "AIMarketingEngine",
            "functions": {
                "ai_marketing_graphql": {
                    "is_static": False,
                    "label": "Marketing GraphQL",
                    "query": [
                        {
                            "action": "question",
                            "label": "View Question",
                        },
                        {
                            "action": "questionList",
                            "label": "View Question List",
                        },
                        {
                            "action": "questionCriteria",
                            "label": "View Question Criteria",
                        },
                        {
                            "action": "questionCriteriaList",
                            "label": "View Question Criteria List",
                        },
                        {
                            "action": "place",
                            "label": "View Question Place",
                        },
                        {
                            "action": "placeList",
                            "label": "View Question Place List",
                        },
                        {
                            "action": "contactProfile",
                            "label": "View Contact Profile",
                        },
                        {
                            "action": "contactProfileList",
                            "label": "View Contact Profile List",
                        },
                        {
                            "action": "CompanyContactProfile",
                            "label": "View Contact Profile Additional Data",
                        },
                        {
                            "action": "CompanyContactProfileList",
                            "label": "View Contact Profile Additional Data List",
                        },
                        {
                            "action": "corporationProfile",
                            "label": "View Corporation Profile",
                        },
                        {
                            "action": "corporationProfileList",
                            "label": "View Corporation Profile List",
                        },
                        {
                            "action": "corporationPlace",
                            "label": "View Corporation Place",
                        },
                        {
                            "action": "corporationPlaceList",
                            "label": "View Corporation Place List",
                        },
                        {
                            "action": "CompanyCorporationProfile",
                            "label": "View Corporation Profile Additional Data",
                        },
                        {
                            "action": "CompanyCorporationProfileList",
                            "label": "View Corporation Profile Additional Data List",
                        },
                        {
                            "action": "contactChatbotHistory",
                            "label": "View Contact Chatbot History",
                        },
                        {
                            "action": "contactChatbotHistoryList",
                            "label": "View Corporation Chatbot History List",
                        },
                        {
                            "action": "utmTagDataCollection",
                            "label": "View Utm Tag Data Collection",
                        },
                        {
                            "action": "utmTagDataCollectionList",
                            "label": "View Utm Tag Data Collection List",
                        },
                    ],
                    "mutation": [
                        {
                            "action": "insertUpdateQuestion",
                            "label": "Create Update Question",
                        },
                        {
                            "action": "deleteQuestion",
                            "label": "Delete Question",
                        },
                        {
                            "action": "insertUpdateQuestionCriteria",
                            "label": "Create Update Question Criteria",
                        },
                        {
                            "action": "deleteQuestionCriteria",
                            "label": "Delete Question Criteria",
                        },
                        {
                            "action": "insertUpdatePlace",
                            "label": "Create Update Place",
                        },
                        {
                            "action": "deletePlace",
                            "label": "Delete Place",
                        },
                        {
                            "action": "insertUpdateContactProfile",
                            "label": "Create Update Contact Profile",
                        },
                        {
                            "action": "deleteContactProfile",
                            "label": "Delete Contact Profile",
                        },
                        {
                            "action": "insertUpdateCompanyContactProfile",
                            "label": "Create Update Contact Profile Additional Data",
                        },
                        {
                            "action": "deleteCompanyContactProfile",
                            "label": "Delete Contact Profile Additional Data",
                        },
                        {
                            "action": "insertUpdateCorporationProfile",
                            "label": "Create Update Corporation Profile",
                        },
                        {
                            "action": "deleteCorporationProfile",
                            "label": "Delete Corporation Profile",
                        },
                        {
                            "action": "insertUpdateCorporationPlace",
                            "label": "Create Update Corporation Place",
                        },
                        {
                            "action": "deleteCorporationPlace",
                            "label": "Delete Corporation Place",
                        },
                        {
                            "action": "insertUpdateCompanyCorporationProfile",
                            "label": "Create Update Corporation Profile Additional Data",
                        },
                        {
                            "action": "deleteCompanyCorporationProfile",
                            "label": "Delete Corporation Profile Additional Data",
                        },
                        {
                            "action": "insertContactChatbotHistory",
                            "label": "Create Contact Chatbot History",
                        },
                        {
                            "action": "deleteContactChatbotHistory",
                            "label": "Delete Contact Chatbot History",
                        },
                        {
                            "action": "insertUtmTagDataCollection",
                            "label": "Create Utm Tag Data Collection",
                        },
                        {
                            "action": "deleteUtmTagDataCollection",
                            "label": "Delete Utm Tag Data Collection",
                        },
                    ],
                    "type": "RequestResponse",
                    "support_methods": ["POST"],
                    "is_auth_required": False,
                    "is_graphql": True,
                    "settings": "beta_core_ai_agent",
                    "disabled_in_resources": True,  # Ignore adding to resource list.
                },
            },
        }
    ]


class AIMarketingEngine(Graphql):
    def __init__(self, logger: logging.Logger, **setting: Dict[str, Any]) -> None:
        Graphql.__init__(self, logger, **setting)

        if (
            setting.get("region_name")
            and setting.get("aws_access_key_id")
            and setting.get("aws_secret_access_key")
        ):
            BaseModel.Meta.region = setting.get("region_name")
            BaseModel.Meta.aws_access_key_id = setting.get("aws_access_key_id")
            BaseModel.Meta.aws_secret_access_key = setting.get("aws_secret_access_key")

        # Initialize configuration via the Config class
        Config.initialize(logger, **setting)

        self.logger = logger
        self.setting = setting

    def ai_marketing_graphql(self, **params: Dict[str, Any]) -> Any:
        ## Test the waters 🧪 before diving in!
        ##<--Testing Data-->##
 
        # if params.get("endpoint_id") is None:
        #     params["endpoint_id"] = self.setting.get("endpoint_id")

        ##<--Testing Data-->##
        schema = Schema(
            query=Query,
            mutation=Mutations,
            types=type_class(),
        )
        return self.execute(schema, **params)
