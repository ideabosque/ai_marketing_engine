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
}

document = Path(
    os.path.join(os.path.dirname(__file__), "ai_marketing_engine.graphql")
).read_text()
sys.path.insert(0, "/var/www/projects/ai_marketing_engine")
sys.path.insert(1, "/var/www/projects/silvaengine_dynamodb_base")

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()

from ai_marketing_engine import AIMarketingEngine


class AIMarketingEngineTest(unittest.TestCase):
    def setUp(self):
        self.ai_marketing_engine = AIMarketingEngine(logger, **setting)
        logger.info("Initiate AIMarketingEngineTest ...")

    def tearDown(self):
        logger.info("Destory AIMarketingEngineTest ...")

    @unittest.skip("demonstrating skipping")
    def test_graphql_ping(self):
        payload = {
            "query": document,
            "variables": {},
            "operation_name": "ping",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_question(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                # "questionUuid": "10575006544938275311",
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
            "operation_name": "insertUpdateQuestion",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_question(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "questionUuid": "10575006544938275311",
            },
            "operation_name": "deleteQuestion",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_question(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "questionUuid": "10575006544938275311",
            },
            "operation_name": "getQuestion",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_question_list(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "questionGroups": ["12345678"],
                "pageNumber": 1,
                "limit": 10,
            },
            "operation_name": "getQuestionList",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_question_criteria(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
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
            "operation_name": "insertUpdateQuestionCriteria",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_question_criteria(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "questionGroup": "XXXXXXXX",
            },
            "operation_name": "deleteQuestionCriteria",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_question_criteria(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "questionGroup": "XXXXXXXX",
            },
            "operation_name": "getQuestionCriteria",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_question_criteria_list(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "region": "XXXXXXXX",
                "questionCriteria": {
                    "place_types": ["abc", "xyz"],
                    "corporation_type": "XXXXXXXX",
                    "corporation_categories": ["XXXXXXXX"],
                    "utm_tag_name": "XXXXXXXX",
                    "corporation_uuid": "4188232447431807471",
                },
                "pageNumber": 1,
                "limit": 10,
            },
            "operation_name": "getQuestionCriteriaList",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_place(self):
        payload = {
            "query": document,
            "variables": {
                "region": "XXXXXXXX",
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
            "operation_name": "insertUpdatePlace",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_place(self):
        payload = {
            "query": document,
            "variables": {
                "region": "XXXXXXXX",
                "placeUuid": "10451635593657061871",
            },
            "operation_name": "deletePlace",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_place(self):
        payload = {
            "query": document,
            "variables": {
                "region": "XXXXXXXX",
                "placeUuid": "16514110523281904111",
            },
            "operation_name": "getPlace",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_place_list(self):
        payload = {
            "query": document,
            "variables": {
                "region": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
            "operation_name": "getPlaceList",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_customer_profile(self):
        payload = {
            "query": document,
            "variables": {
                "placeUuid": "6605612459024716271",
                # "customerUuid": "15540923710806430191",
                "email": "XXXXXXXX",
                "region": "XXXXXXXX",
                # "firstName": "XXXXXXXX",
                # "lastName": "XXXXXXXX",
                # "data": {},
                "updatedBy": "XYZ",
            },
            "operation_name": "insertUpdateCustomerProfile",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_customer_profile(self):
        payload = {
            "query": document,
            "variables": {
                "placeUuid": "16514110523281904111",
                "customerUuid": "14431819951939916271",
            },
            "operation_name": "deleteCustomerProfile",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_customer_profile(self):
        payload = {
            "query": document,
            "variables": {
                "placeUuid": "16514110523281904111",
                "customerUuid": "12355966540142023151",
            },
            "operation_name": "getCustomerProfile",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_customer_profile_list(self):
        payload = {
            "query": document,
            "variables": {
                "placeUuid": "16514110523281904111",
                "pageNumber": 1,
                "limit": 10,
            },
            "operation_name": "getCustomerProfileList",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_company_customer_profile(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "customerUuid": "15540923710806430191",
                "placeUuid": "6605612459024716271",
                "email": "XXXXXXXX",
                "corporationType": "XXXXXXXX",
                "corporationUuid": "10077997009953100271",
                "data": {},
                "updatedBy": "XYZ",
            },
            "operation_name": "insertUpdateCompanyCustomerProfiles",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_company_customer_profile(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "customerUuid": "12355966540142023151",
            },
            "operation_name": "deleteCompanyCustomerProfiles",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_company_customer_profile(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "customerUuid": "12355966540142023151",
            },
            "operation_name": "getCompanyCustomerProfiles",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_company_customer_profile_list(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
            "operation_name": "getCompanyCustomerProfilesList",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_corporation_profile(self):
        payload = {
            "query": document,
            "variables": {
                "corporationType": "XXXXXXXX",
                "corporationUuid": "10077997009953100271",
                "externalId": "XXXXXXXX",
                "businessName": "XXXXXXXX",
                "categories": ["XXXXXXXX"],
                "address": {},
                "data": {},
                "updatedBy": "XYZ",
            },
            "operation_name": "insertUpdateCorporationProfile",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_corporation_profile(self):
        payload = {
            "query": document,
            "variables": {
                "corporationType": "XXXXXXXX",
                "corporationUuid": "4188232447431807471",
            },
            "operation_name": "deleteCorporationProfile",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_corporation_profile(self):
        payload = {
            "query": document,
            "variables": {
                "corporationType": "XXXXXXXX",
                "corporationUuid": "4188232447431807471",
            },
            "operation_name": "getCorporationProfile",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_corporation_profile_list(self):
        payload = {
            "query": document,
            "variables": {
                "corporationType": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
            "operation_name": "getCorporationProfileList",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_corporation_place(self):
        payload = {
            "query": document,
            "variables": {
                "region": "XXXXXXXX",
                "corporationUuid": "10077997009953100271",
                "placeUuid": "6605612459024716271",
                "corporationType": "XXXXXXXX",
                "updatedBy": "XYZ",
            },
            "operation_name": "insertUpdateCorporationPlace",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_corporation_place(self):
        payload = {
            "query": document,
            "variables": {
                "corporationUuid": "XXXXXXXX",
                "placeUuid": "XXXXXXXXXXXXXXXXXXX",
            },
            "operation_name": "deleteCorporationPlace",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_corporation_place(self):
        payload = {
            "query": document,
            "variables": {
                "corporationUuid": "4188232447431807471",
                "placeUuid": "16514110523281904111",
            },
            "operation_name": "getCorporationPlace",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_corporation_place_list(self):
        payload = {
            "query": document,
            "variables": {
                "corporationUuid": "4188232447431807471",
                "pageNumber": 1,
                "limit": 10,
            },
            "operation_name": "getCorporationPlaceList",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    # @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_company_corporation_profile(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "corporationUuid": "10077997009953100271",
                "externalId": "XXXXXXXX",
                "corporationType": "XXXXXXXX",
                "data": {},
                "updatedBy": "XYZ",
            },
            "operation_name": "insertUpdateCompanyCorporationProfiles",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_company_corporation_profile(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "corporationUuid": "4188232447431807471",
            },
            "operation_name": "deleteCompanyCorporationProfiles",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_company_corporation_profile(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "corporationUuid": "4188232447431807471",
            },
            "operation_name": "getCompanyCorporationProfiles",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_company_corporation_profile_list(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
            "operation_name": "getCompanyCorporationProfilesList",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_customer_chatbot_history(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "timestamp": 1724514266,
                "customerUuid": "XXXXXXXX",
                "placeUuid": "XXXXXXXX",
                "region": "XXXXXXXX",
                "assistantId": "XXXXXXXX",
                "threadId": "XXXXXXXX",
                "assistantType": "XXXXXXXX",
            },
            "operation_name": "insertCustomerChatbotHistory",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_customer_chatbot_history(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "timestamp": 1724514266,
            },
            "operation_name": "deleteCustomerChatbotHistory",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_customer_chatbot_history(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "timestamp": 1724514266,
            },
            "operation_name": "getCustomerChatbotHistory",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_customer_chatbot_history_list(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
            "operation_name": "getCustomerChatbotHistoryList",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_utm_tag_data_collection(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "tagName": "XXXXXXXX",
                "customerUuid": "15540923710806430191",
                "placeUuid": "6605612459024716271",
                "region": "XXXXXXXX",
                "keyword": "XXXXXXXX",
                "utmCampaign": "XXXXXXXX",
                "utmContent": "XXXXXXXX",
                "utmMedium": "XXXXXXXX",
                "utmSource": "XXXXXXXX",
                "utmTerm": "XXXXXXXX",
            },
            "operation_name": "insertUtmTagDataCollection",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_utm_tag_data_collection(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "collectionUuid": "359510789495853551",
            },
            "operation_name": "deleteUtmTagDataCollection",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_utm_tag_data_collection(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "collectionUuid": "15513258872781541871",
            },
            "operation_name": "getUtmTagDataCollection",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_utm_tag_data_collection_list(self):
        payload = {
            "query": document,
            "variables": {
                "companyId": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
            "operation_name": "getUtmTagDataCollectionList",
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)


if __name__ == "__main__":
    unittest.main()
