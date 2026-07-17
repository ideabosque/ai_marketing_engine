#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
from typing import Any, Dict, List

from graphene import Schema

from silvaengine_dynamodb_base import BaseModel
from silvaengine_utility import Graphql

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

    def _apply_partition_defaults(self, params: Dict[str, Any]) -> None:
        """
        Apply default partition values if not provided in params.

        Args:
            params (Dict[str, Any]): A dictionary of parameters required to build the GraphQL query.
        """
        if params.get("context") is None:
            params["context"] = {}

        context = params["context"]
        endpoint_id = (
            context["endpoint_id"]
            if "endpoint_id" in context
            else params.get("endpoint_id", self.setting.get("endpoint_id"))
        )
        part_id = (
            context["part_id"]
            if "part_id" in context
            else params.get("metadata", {}).get(
                "part_id",
                params.get("part_id", self.setting.get("part_id")),
            )
        )

        if "endpoint_id" not in context:
            context["endpoint_id"] = endpoint_id
        if "part_id" not in context:
            context["part_id"] = part_id
        if "connection_id" not in params:
            params["connection_id"] = self.setting.get("connection_id")

        if not endpoint_id or not part_id:
            self.logger.error(
                f"Missing endpoint_id or part_id: endpoint_id={endpoint_id}, part_id={part_id}"
            )
            raise ValueError(
                "Both 'endpoint_id' and 'part_id' are required to generate 'partition_key'."
            )

        context["partition_key"] = f"{endpoint_id}#{part_id}"

        if "logger" in params:
            params.pop("logger")
        if "setting" in params:
            params.pop("setting")
    def ai_marketing_graphql(self, **params: Dict[str, Any]) -> Any:
        self._apply_partition_defaults(params)

        # In PostgreSQL mode, set the RLS tenant context for this request and
        # tear down the scoped session afterwards. No-op in DynamoDB mode.
        partition_key = params.get("context", {}).get("partition_key")
        if partition_key and Config.DB_BACKEND == "postgresql":
            Config._set_rls_context(partition_key)

        try:
            return self.execute(self.__class__.build_graphql_schema(), **params)
        finally:
            if Config.DB_BACKEND == "postgresql" and Config.db_session:
                Config.db_session.remove()

    @staticmethod
    def build_graphql_schema() -> Schema:
        return Schema(
            query=Query,
            mutation=Mutations,
            types=type_class(),
        )


# ---------------------------------------------------------------------------
# Module-level dispatch functions for gateway integration
# ---------------------------------------------------------------------------
# Called by silvaengine_gateway via the route manifest's ``dispatch`` field
# (e.g. "ai_marketing_engine.main:dispatch_graphql"). Builds a short-lived
# engine from the already-initialized Config singleton.
# ---------------------------------------------------------------------------


def dispatch_graphql(**params: Any) -> Any:
    """Execute a GraphQL query/mutation against the AI Marketing Engine.

    Requires ``Config.initialize()`` to have been called (done by gateway
    startup). On the PostgreSQL backend, RLS tenant context is set from
    ``partition_key`` inside ``ai_marketing_graphql`` and the scoped session
    is rolled back on error and removed after the request. (No-op on the
    DynamoDB backend, where ``db_session`` is ``None``.)
    """
    logger = Config.get_logger()
    instance = AIMarketingEngine(logger, **Config.get_setting())
    db_session = Config.db_session
    try:
        return instance.ai_marketing_graphql(**params)
    except Exception:
        if db_session is not None:
            db_session.rollback()
        raise
    finally:
        if db_session is not None:
            db_session.remove()
