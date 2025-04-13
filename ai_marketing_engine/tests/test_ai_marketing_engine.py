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
    "aws_s3_bucket": os.getenv("aws_s3_bucket"),
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
    def test_graphql_presigned_upload_url(self):
        query = Utility.generate_graphql_operation(
            "presignedUploadUrl", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "objectKey": "test.txt",
            },
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
    def test_graphql_insert_update_question_group(self):
        query = Utility.generate_graphql_operation(
            "insertUpdateQuestionGroup", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "questionGroupUuid": "15006769565442904560",
                "questionGroupName": "XXXXXXXX",
                "questionGroupDescription": "XXXXXXXX",
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
    def test_graphql_delete_question_group(self):
        query = Utility.generate_graphql_operation(
            "deleteQuestionGroup", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "questionGroupUuid": "8734185510007607792",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_question_group(self):
        query = Utility.generate_graphql_operation(
            "questionGroup", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "questionGroupUuid": "15006769565442904560",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_question_group_list(self):
        query = Utility.generate_graphql_operation(
            "questionGroupList", "Query", self.schema
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
    def test_graphql_insert_update_wizard(self):
        query = Utility.generate_graphql_operation(
            "insertUpdateWizard", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "wizardUuid": "1943415144959382000",
                "questionGroupUuid": "15006769565442904560",
                "wizardTitle": "XXXXXXXX",
                "wizardDescription": "XXXXXXXX",
                "wizardType": "page",
                # "formSchema": None,
                # "embedContent": None,
                # "priority": 0,
                "updatedBy": "XYZ",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_wizard(self):
        query = Utility.generate_graphql_operation(
            "deleteWizard", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "wizardUuid": "2325624121421009392",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    # @unittest.skip("demonstrating skipping")
    def test_graphql_wizard(self):
        query = Utility.generate_graphql_operation("wizard", "Query", self.schema)
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "wizardUuid": "1943415144959382000",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_wizard_list(self):
        query = Utility.generate_graphql_operation("wizardList", "Query", self.schema)
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "questionGroupUuid": "15006769565442904560",
                "pageNumber": 1,
                "limit": 10,
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
                "questionUuid": "115703653371220464",
                "questionGroupUuid": "15006769565442904560",
                "wizardUuid": "1943415144959382000",
                "dataType": "contact",
                "question": "Can you provide your sales certification?",
                "priority": 6,
                "attributeName": "sales_certification",
                "attributeType": "file",
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
                "questionUuid": "115703653371220464",
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
                "questionGroupUuid": "15006769565442904560",
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
                "placeUuid": "10869587599689126384",
                "region": "US",
                "latitude": "XXXXXXXX",
                "longitude": "XXXXXXXX",
                "businessName": "XXXXXXXX",
                "address": "XXXXXXXX",
                "phoneNumber": "XXXXXXXX",
                "website": "XXXXXXXX",
                "types": ["abc", "xyz"],
                "corporationUuid": "11884466832473330160",
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
                "placeUuid": "5277338226639835632",
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
                "placeUuid": "10869587599689126384",
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
                "region": "US",
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
                "placeUuid": "10869587599689126384",
                "contactUuid": "16754529983121134064",
                "email": "XXXXXXXX",
                "region": "US",
                "firstName": "XXXXXXXX",
                "lastName": "XXXXXXXX",
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
                "placeUuid": "10869587599689126384",
                "contactUuid": "4715411733862355440",
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
                "placeUuid": "10869587599689126384",
                "contactUuid": "16754529983121134064",
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
                "placeUuid": "10869587599689126384",
                "email": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_insert_update_contact_request(self):
        query = Utility.generate_graphql_operation(
            "insertUpdateContactRequest", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "contactUuid": "16754529983121134064",
                "requestUuid": "10080978926371672560",
                "placeUuid": "10869587599689126384",
                "requestTitle": "XXXXXXXX",
                "requestDetail": "XXXXXXXX",
                "updatedBy": "XYZ",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_contact_request(self):
        query = Utility.generate_graphql_operation(
            "deleteContactRequest", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "contactUuid": "16754529983121134064",
                "requestUuid": "13138863480685007344",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_contact_request(self):
        query = Utility.generate_graphql_operation(
            "contactRequest", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "contactUuid": "16754529983121134064",
                "requestUuid": "10080978926371672560",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_contact_request_list(self):
        query = Utility.generate_graphql_operation(
            "contactRequestList", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "contactUuid": "16754529983121134064",
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
                "corporationUuid": "11884466832473330160",
                "externalId": "XXXXXXXX",
                "corporationType": "XXXXXXXX",
                "businessName": "XXXXXXXX",
                "categories": ["XXXXXXXX"],
                "address": {},
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
                "corporationUuid": "88364932402975216",
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
                "corporationUuid": "8205577994827928048",
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
    def test_graphql_insert_update_attribute_value(self):
        query = Utility.generate_graphql_operation(
            "insertUpdateAttributeValue", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "dataTypeAttributeName": "contact-role_type",
                # "valueVersionUuid": "13420102135434449392",
                "dataIdentity": "16754529983121134064",
                "value": "buyer",
                "updatedBy": "XYZ",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_delete_attribute_value(self):
        query = Utility.generate_graphql_operation(
            "deleteAttributeValue", "Mutation", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "dataTypeAttributeName": "contact-role_type",
                "valueVersionUuid": "13420102135434449392",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_attribute_value(self):
        query = Utility.generate_graphql_operation(
            "attributeValue", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "dataTypeAttributeName": "contact-role_type",
                "valueVersionUuid": "10517417074765599216",
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_attribute_value_list(self):
        query = Utility.generate_graphql_operation(
            "attributeValueList", "Query", self.schema
        )
        logger.info(f"Query: {query}")
        payload = {
            "query": query,
            "variables": {
                "dataTypeAttributeName": "contact-role_type",
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
                "collectionUuid": "4686129127874957808",
                "tagName": "XXXXXXXX",
                "placeUuid": "10869587599689126384",
                "contactUuid": "16754529983121134064",
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
                "collectionUuid": "9202569066782986736",
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
                "collectionUuid": "4686129127874957808",
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
                "tagName": "XXXXXXXX",
                "pageNumber": 1,
                "limit": 10,
            },
        }
        response = self.ai_marketing_engine.ai_marketing_graphql(**payload)
        logger.info(response)


if __name__ == "__main__":
    unittest.main()
