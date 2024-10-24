#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
from typing import Any, Dict, List

from graphene import Schema
from silvaengine_dynamodb_base import SilvaEngineDynamoDBBase

from .handlers import handlers_init
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
                            "action": "customerProfile",
                            "label": "View Customer Profile",
                        },
                        {
                            "action": "customerProfileList",
                            "label": "View Customer Profile List",
                        },
                        {
                            "action": "CompanyCustomerProfiles",
                            "label": "View Customer Profile Additional Data",
                        },
                        {
                            "action": "CompanyCustomerProfilesList",
                            "label": "View Customer Profile Additional Data List",
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
                            "action": "CompanyCorporationProfiles",
                            "label": "View Corporation Profile Additional Data",
                        },
                        {
                            "action": "CompanyCorporationProfilesList",
                            "label": "View Corporation Profile Additional Data List",
                        },
                        {
                            "action": "customerChatbotHistory",
                            "label": "View Customer Chatbot History",
                        },
                        {
                            "action": "customerChatbotHistoryList",
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
                            "action": "insertUpdateCustomerProfile",
                            "label": "Create Update Customer Profile",
                        },
                        {
                            "action": "deleteCustomerProfile",
                            "label": "Delete Customer Profile",
                        },
                        {
                            "action": "insertUpdateCompanyCustomerProfiles",
                            "label": "Create Update Customer Profile Additional Data",
                        },
                        {
                            "action": "deleteCompanyCustomerProfiles",
                            "label": "Delete Customer Profile Additional Data",
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
                            "action": "insertUpdateCompanyCorporationProfiles",
                            "label": "Create Update Corporation Profile Additional Data",
                        },
                        {
                            "action": "deleteCompanyCorporationProfiles",
                            "label": "Delete Corporation Profile Additional Data",
                        },
                        {
                            "action": "insertCustomerChatbotHistory",
                            "label": "Create Customer Chatbot History",
                        },
                        {
                            "action": "deleteCustomerChatbotHistory",
                            "label": "Delete Customer Chatbot History",
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
                    "settings": "ai_marketing_engine",
                    "disabled_in_resources": True,  # Ignore adding to resource list.
                },
            },
        }
    ]


class AIMarketingEngine(SilvaEngineDynamoDBBase):
    def __init__(self, logger: logging.Logger, **setting: Dict[str, Any]) -> None:
        handlers_init(logger, **setting)

        self.logger = logger
        self.setting = setting

        SilvaEngineDynamoDBBase.__init__(self, logger, **setting)

    def ai_marketing_graphql(self, **params: Dict[str, Any]) -> Any:
        schema = Schema(
            query=Query,
            mutation=Mutations,
            types=type_class(),
        )
        return self.graphql_execute(schema, **params)
