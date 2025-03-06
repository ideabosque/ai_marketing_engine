#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import json
import logging
import os
import sys
import time
import unittest
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
setting = {
    "region_name": os.getenv("region_name"),
    "aws_access_key_id": os.getenv("aws_access_key_id"),
    "aws_secret_access_key": os.getenv("aws_secret_access_key"),
    "functs_on_local": {
        "ai_marketing_graphql": {
            "module_name": "ai_marketing_engine",
            "class_name": "AIMarketingEngine",
        },
    },
    "endpoint_id": os.getenv("endpoint_id"),
    "test_mode": os.getenv("test_mode"),
}

sys.path.insert(0, f"{os.getenv('BASE_DIR')}/ai_marketing_engine")
sys.path.insert(1, f"{os.getenv('BASE_DIR')}/silvaengine_dynamodb_base")

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()

from ai_marketing_engine import AIMarketingEngine
from silvaengine_utility import Utility


class AIMarketingEngineTest(unittest.TestCase):
    def setUp(self):
        self.ai_marketing_engine = AIMarketingEngine(logger, **setting)
        endpoint_id = setting.get("endpoint_id")
        test_mode = setting.get("test_mode")
        self.schema = Utility.fetch_graphql_schema(
            logger,
            endpoint_id,
            "ai_marketing_graphql",
            setting=setting,
            test_mode=test_mode,
        )
        logger.info("Initiate AIMarketingEngineTest ...")

    def tearDown(self):
        logger.info("Destory AIMarketingEngineTest ...")

    @unittest.skip("demonstrating skipping")
    def test_graphql_ping(self):
        query = Utility.generate_graphql_operation("ping", "Query", self.schema)
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {},
            "operation_name": "ping",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_activity_history(self):
        query = Utility.generate_graphql_operation(
            "insertActivityHistory", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "id": "company_contact_profile-openai-9687284472428368367",
                "dataDiff": {
                    "values_changed": {
                        "root['data']['product_name']": {
                            "new_value": "toy",
                            "old_value": "clothes",
                        }
                    }
                },
                "log": "The company_contact_profile with the endpoint_id/contact_uuid (openai/9687284472428368367) is updated at 4:24:00.",
                "type": "company_contact_profile",
                "updatedBy": "XYZ",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_activity_history(self):
        query = Utility.generate_graphql_operation(
            "deleteActivityHistory", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "id": "company_contact_profile-openai-9687284472428368367",
                "timestamp": "1741220959",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_activity_history(self):
        query = Utility.generate_graphql_operation(
            "activityHistory", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "id": "company_contact_profile-openai-9687284472428368367",
                "timestamp": "1741200290",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_activity_history_list(self):
        query = Utility.generate_graphql_operation(
            "activityHistoryList", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "id": "company_contact_profile-openai-9687284472428368367",
                "limit": 10,
                "offset": 0,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_question(self):
        query = Utility.generate_graphql_operation(
            "insertUpdateQuestion", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "questionUuid": "17090916094743351791",
                "questionGroup": "12345678",
                "question": "What is the material you interested?",
                "priority": 5,
                "attribute": "material",
                # "optionValues": [
                #     "white",
                #     "black",
                #     "gray",
                #     "red",
                #     "blue",
                #     "green",
                #     "yellow",
                #     "orange",
                #     "purple",
                #     "pink",
                #     "brown",
                #     "beige",
                #     "gold",
                #     "silver",
                #     "other",
                # ],
                # "condition": [
                #     {"attribute": "product_name", "value": ["clothes"]},
                # ],
                "updatedBy": "XYZ",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_question(self):
        query = Utility.generate_graphql_operation(
            "deleteQuestion", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "questionUuid": "9872603553811337711",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_question(self):
        query = Utility.generate_graphql_operation("question", "Query", self.schema)
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "questionUuid": "17090916094743351791",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_question_list(self):
        query = Utility.generate_graphql_operation("questionList", "Query", self.schema)
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "questionGroups": ["12345678"],
                "pageNumber": 1,
                "limit": 10,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_question_criteria(self):
        query = Utility.generate_graphql_operation(
            "insertUpdateQuestionCriteria", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "questionGroup": "12345678",
                "region": "US",
                "questionCriteria": {
                    "place_type": "establishment",
                    "corporation_type": "XXXXXXXX",
                    # "corporation_category": "XXXXXXXX",
                    # "utm_tag_name": "XXXXXXXX",
                    # "corporation_uuids": ["4188232447431807471"],
                },
                "weight": 0,
                "updatedBy": "XYZ",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_question_criteria(self):
        query = Utility.generate_graphql_operation(
            "deleteQuestionCriteria", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "companyId": "XXXXXXXX",
                "questionGroup": "XXXXXXXX",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_question_criteria(self):
        query = Utility.generate_graphql_operation(
            "questionCriteria", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "questionGroup": "12345678",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_question_criteria_list(self):
        query = Utility.generate_graphql_operation(
            "questionCriteriaList", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "region": "US",
                "questionCriteria": {
                    # "place_types": ["abc", "xyz"],
                    # "corporation_type": "XXXXXXXX",
                    # "corporation_categories": ["XXXXXXXX"],
                    # "utm_tag_name": "XXXXXXXX",
                    # "corporation_uuid": "4188232447431807471",
                },
                "pageNumber": 1,
                "limit": 10,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_place(self):
        query = Utility.generate_graphql_operation(
            "insertUpdatePlace", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "region": "US",
                # "placeUuid": "16514110523281904111",
                "latitude": "XXXXXXXX",
                "longitude": "XXXXXXXX",
                "businessName": "XXXXXXXX",
                "address": "XXXXXXXX",
                "phoneNumber": "XXXXXXXX",
                "website": "XXXXXXXX",
                "types": ["abc", "xyz"],
                "updatedBy": "XYZ",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_place(self):
        query = Utility.generate_graphql_operation(
            "deletePlace", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "region": "XXXXXXXX",
                "placeUuid": "10451635593657061871",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_place(self):
        query = Utility.generate_graphql_operation("place", "Query", self.schema)
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "region": "XXXXXXXX",
                "placeUuid": "16514110523281904111",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_place_list(self):
        query = Utility.generate_graphql_operation("placeList", "Query", self.schema)
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "region": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_contact_profile(self):
        query = Utility.generate_graphql_operation(
            "insertUpdateContactProfile", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "placeUuid": "7888864077977555439",
                "contactUuid": "6676570951220597231",
                "email": "XXXXXXXX",
                "region": "US",
                # "firstName": "XXXXXXXX",
                # "lastName": "XXXXXXXX",
                # "corporationType": "XXXXXXXX",
                # "corporationUuid": "10077997009953100271",
                # "data": {},
                "updatedBy": "XYZ",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_contact_profile(self):
        query = Utility.generate_graphql_operation(
            "deleteContactProfile", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "placeUuid": "16514110523281904111",
                "contactUuid": "7942627832711090671",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_contact_profile(self):
        query = Utility.generate_graphql_operation(
            "contactProfile", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "placeUuid": "16514110523281904111",
                "contactUuid": "12355966540142023151",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_contact_profile_list(self):
        query = Utility.generate_graphql_operation(
            "contactProfileList", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "placeUuid": "2182613588100714991",
                "email": "bibo72@outlook.com",
                "pageNumber": 1,
                "limit": 10,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    # @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_company_contact_profile(self):
        query = Utility.generate_graphql_operation(
            "insertUpdateCompanyContactProfile", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "contactUuid": "9687284472428368367",
                "placeUuid": "11580716724379521519",
                "email": "bibo72@outlook.com",
                "data": {"product_name": "toy"},
                "updatedBy": "XYZ",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_company_contact_profile(self):
        query = Utility.generate_graphql_operation(
            "deleteCompanyContactProfile", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "companyId": "XXXXXXXX",
                "contactUuid": "12355966540142023151",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_company_contact_profile(self):
        query = Utility.generate_graphql_operation(
            "companyContactProfile", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "companyId": "XXXXXXXX",
                "contactUuid": "7942627832711090671",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_company_contact_profile_list(self):
        query = Utility.generate_graphql_operation(
            "companyContactProfileList", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "companyId": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_company_contact_request(self):
        query = Utility.generate_graphql_operation(
            "insertUpdateCompanyContactRequest", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "contactUuid": "6676570951220597231",
                # "requestUuid": "13024172026426298863",
                "requestTitle": "XXXXXXXX",
                "requestDetail": "XXXXXXXX",
                "updatedBy": "XYZ",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_company_contact_request(self):
        query = Utility.generate_graphql_operation(
            "deleteCompanyContactRequest", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "contactUuid": "136056295826461167",
                "requestUuid": "13024172026426298863",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_company_contact_request(self):
        query = Utility.generate_graphql_operation(
            "companyContactRequest", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "contactUuid": "136056295826461167",
                "requestUuid": "13024172026426298863",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_company_contact_request_list(self):
        query = Utility.generate_graphql_operation(
            "companyContactRequestList", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "contactUuid": "136056295826461167",
                "companyId": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_corporation_profile(self):
        query = Utility.generate_graphql_operation(
            "insertUpdateCorporationProfile", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "corporationType": "XXXXXXXX",
                # "corporationUuid": "10077997009953100271",
                "externalId": "XXXXXXXX",
                "businessName": "XXXXXXXX",
                "categories": ["XXXXXXXX"],
                "address": {},
                "data": {},
                "updatedBy": "XYZ",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_corporation_profile(self):
        query = Utility.generate_graphql_operation(
            "deleteCorporationProfile", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "corporationType": "XXXXXXXX",
                "corporationUuid": "4188232447431807471",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_corporation_profile(self):
        query = Utility.generate_graphql_operation(
            "corporationProfile", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "corporationType": "XXXXXXXX",
                "corporationUuid": "4188232447431807471",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_corporation_profile_list(self):
        query = Utility.generate_graphql_operation(
            "corporationProfileList", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "corporationType": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_corporation_place(self):
        query = Utility.generate_graphql_operation(
            "insertUpdateCorporationPlace", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "region": "US",
                "corporationUuid": "7839731756645421551",
                "placeUuid": "7888864077977555439",
                "corporationType": "XXXXXXXX",
                "updatedBy": "XYZ",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_corporation_place(self):
        query = Utility.generate_graphql_operation(
            "deleteCorporationPlace", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "corporationUuid": "XXXXXXXX",
                "placeUuid": "XXXXXXXXXXXXXXXXXXX",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_corporation_place(self):
        query = Utility.generate_graphql_operation(
            "corporationPlace", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "corporationUuid": "4188232447431807471",
                "placeUuid": "16514110523281904111",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_corporation_place_list(self):
        query = Utility.generate_graphql_operation(
            "corporationPlaceList", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "corporationUuid": "4188232447431807471",
                "pageNumber": 1,
                "limit": 10,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_company_corporation_profile(self):
        query = Utility.generate_graphql_operation(
            "insertUpdateCompanyCorporationProfile", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "corporationUuid": "7839731756645421551",
                "externalId": "XXXXXXXX",
                "corporationType": "XXXXXXXX",
                "data": {},
                "updatedBy": "XYZ",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_company_corporation_profile(self):
        query = Utility.generate_graphql_operation(
            "deleteCompanyCorporationProfile", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "companyId": "XXXXXXXX",
                "corporationUuid": "4188232447431807471",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_company_corporation_profile(self):
        query = Utility.generate_graphql_operation(
            "companyCorporationProfile", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "companyId": "XXXXXXXX",
                "corporationUuid": "4188232447431807471",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_company_corporation_profile_list(self):
        query = Utility.generate_graphql_operation(
            "companyCorporationProfileList", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "companyId": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_contact_chatbot_history(self):
        query = Utility.generate_graphql_operation(
            "insertContactChatbotHistory", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "timestamp": 1724514266,
                "contactUuid": "6676570951220597231",
                "placeUuid": "7888864077977555439",
                "region": "US",
                "assistantId": "XXXXXXXX",
                "threadId": "XXXXXXXX",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_contact_chatbot_history(self):
        query = Utility.generate_graphql_operation(
            "deleteContactChatbotHistory", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "companyId": "XXXXXXXX",
                "timestamp": 1724514266,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_contact_chatbot_history(self):
        query = Utility.generate_graphql_operation(
            "contactChatbotHistory", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "companyId": "XXXXXXXX",
                "timestamp": 1724514266,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_contact_chatbot_history_list(self):
        query = Utility.generate_graphql_operation(
            "contactChatbotHistoryList", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "companyId": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_utm_tag_data_collection(self):
        query = Utility.generate_graphql_operation(
            "insertUtmTagDataCollection", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "tagName": "XXXXXXXX",
                "contactUuid": "7888864077977555439",
                "placeUuid": "7888864077977555439",
                "region": "US",
                "keyword": "XXXXXXXX",
                "utmCampaign": "XXXXXXXX",
                "utmContent": "XXXXXXXX",
                "utmMedium": "XXXXXXXX",
                "utmSource": "XXXXXXXX",
                "utmTerm": "XXXXXXXX",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_utm_tag_data_collection(self):
        query = Utility.generate_graphql_operation(
            "deleteUtmTagDataCollection", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "companyId": "XXXXXXXX",
                "collectionUuid": "359510789495853551",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_utm_tag_data_collection(self):
        query = Utility.generate_graphql_operation(
            "utmTagDataCollection", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "companyId": "XXXXXXXX",
                "collectionUuid": "15513258872781541871",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_utm_tag_data_collection_list(self):
        query = Utility.generate_graphql_operation(
            "utmTagDataCollectionList", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "companyId": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)


if __name__ == "__main__":
    unittest.main()
