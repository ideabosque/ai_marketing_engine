#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Load sample data into the AI Marketing Engine following the model priority from README:

1. CorporationProfile (root)
2. Place (depends on CorporationProfile)
3. ContactProfile (depends on Place)
4. ContactRequest (depends on ContactProfile + Place)

The script mirrors the structure used in ai_rfq_engine/tests/load_sample_data.py:
- Loads environment from tests/.env
- Initializes AIMarketingEngine with local settings
- Executes GraphQL mutations in dependency order
- Persists the returned IDs into test_data.json for tests to reuse
"""
from __future__ import annotations

import json
import logging
import os
import random
import sys
import uuid
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Load .env from current (tests) directory before setting up paths
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)

# Ensure local packages are importable (mirrors conftest.py setup)
def _normalize_base_dir(raw_path: Optional[str]) -> Optional[str]:
    """Normalize base_dir from env (supports Windows-style paths under WSL)."""
    if not raw_path:
        return None
    expanded = os.path.expanduser(raw_path)
    if os.path.isdir(expanded):
        return expanded

    # Translate Windows-style paths (e.g., C:/Users/...) to WSL (/mnt/c/Users/...)
    if len(expanded) > 2 and expanded[1] == ":":
        drive = expanded[0].lower()
        remainder = expanded[2:].lstrip("\\/").replace("\\", "/")
        candidate = os.path.join("/mnt", drive, remainder)
        if os.path.isdir(candidate):
            return candidate
    return None


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
monorepo_root = os.path.abspath(os.path.join(project_root, ".."))
env_base_dir = _normalize_base_dir(os.getenv("base_dir"))
BASE_DIR = (
    env_base_dir
    or (monorepo_root if os.path.isdir(os.path.join(monorepo_root, "silvaengine_dynamodb_base")) else project_root)
)
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "silvaengine_utility"))
sys.path.insert(1, os.path.join(BASE_DIR, "silvaengine_dynamodb_base"))
sys.path.insert(2, os.path.join(BASE_DIR, "ai_marketing_engine"))

from ai_marketing_engine import AIMarketingEngine  # noqa: E402
from silvaengine_utility import Utility  # noqa: E402

try:
    from faker import Faker

    fake = Faker()
except ModuleNotFoundError:
    print(
        "The 'faker' package is not installed. Please install it by running 'pip install faker'."
    )
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("load_sample_data")

# --- CONFIGURATION ---
ENDPOINT_ID = os.getenv("endpoint_id")
UPDATED_BY = os.getenv("updated_by", "data_loader_script")
TEST_DATA_FILE = os.path.join(os.path.dirname(__file__), "test_data.json")

SETTING = {
    "region_name": os.getenv("region_name"),
    "aws_access_key_id": os.getenv("aws_access_key_id"),
    "aws_secret_access_key": os.getenv("aws_secret_access_key"),
    "functs_on_local": {
        "ai_marketing_graphql": {
            "module_name": "ai_marketing_engine",
            "class_name": "AIMarketingEngine",
        },
    },
    "endpoint_id": ENDPOINT_ID,
    "execute_mode": os.getenv("execute_mode", "local"),
}


def create_engine() -> AIMarketingEngine:
    """Instantiate AIMarketingEngine using environment-driven settings."""
    try:
        engine = AIMarketingEngine(logger, **SETTING)
        setattr(engine, "__is_real__", True)
        return engine
    except Exception as exc:  # pragma: no cover - runtime safeguard
        logger.error(f"Failed to initialize AIMarketingEngine: {exc}", exc_info=True)
        raise


def run_graphql_mutation(
    engine: AIMarketingEngine,
    query: str,
    variables: Dict[str, Any],
    label: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Execute a GraphQL mutation through the local engine."""
    op = label or query.strip().splitlines()[0]
    try:
        response = engine.ai_marketing_graphql(
            query=query,
            variables=variables,
            endpoint_id=ENDPOINT_ID,
        )
        parsed = (
            Utility.json_loads(response)
            if isinstance(response, (str, bytes))
            else response
        )
    except Exception as exc:
        logger.error(f"[{op}] GraphQL execution failed: {exc}", exc_info=True)
        return None

    if parsed.get("errors"):
        # Use str() to handle Decimal and other non-JSON-serializable types
        logger.error("[%s] GraphQL Error: %s", op, str(parsed["errors"]))
        return None

    data = parsed.get("data")
    if not data:
        logger.error("[%s] GraphQL Error: No data returned.", op)
        return None

    logger.info("[%s] Success", op)
    return data


def load_existing_test_data() -> Dict[str, Any]:
    """Load existing test data so unrelated fixtures are preserved."""
    if not os.path.exists(TEST_DATA_FILE):
        return {}
    try:
        with open(TEST_DATA_FILE, "r") as f:
            return json.load(f)
    except (ValueError, OSError):
        logger.warning("Could not read existing test data. Creating a fresh file.")
        return {}


def persist_test_data(test_data_updates: Dict[str, Any]) -> None:
    """Override test_data.json with newly generated data."""
    # For each entity type, randomly select one entry for get/list test data
    final_data = {}

    for key, records in test_data_updates.items():
        if not records:
            continue

        # For main test data, include all records
        if not key.endswith('_get_test_data') and not key.endswith('_list_test_data'):
            final_data[key] = records
        # For get/list test data, randomly pick one entry
        else:
            final_data[key] = [random.choice(records)]

    with open(TEST_DATA_FILE, "w") as f:
        json.dump(final_data, f, indent=2)
    print(f"\nTest data written to: {TEST_DATA_FILE}")


def generate_corporation_profile_flow_case() -> Dict[str, Any]:
    """Create insert/update payloads for corporation profile flow test."""
    external_id = f"EXT-TEST-{fake.random_number(digits=6, fix_len=True)}"
    corporation_type = fake.random_element(["private", "public", "nonprofit"])
    initial_business_name = fake.company()
    updated_business_name = f"Updated {initial_business_name}"

    industry = fake.random_element(["Technology", "Finance", "Healthcare", "Retail"])
    initial_employee_count = str(fake.random_int(min=10, max=500))
    updated_employee_count = str(fake.random_int(min=500, max=5000))
    founded_year = str(fake.random_int(min=1990, max=2020))

    city = fake.city()
    state = fake.state_abbr()

    return {
        "insert_data": {
            "externalId": external_id,
            "corporationType": corporation_type,
            "businessName": initial_business_name,
            "categories": ["technology"],
            "address": {
                "street": fake.street_address(),
                "city": city,
                "state": state,
                "zip": fake.zipcode(),
            },
            "updatedBy": UPDATED_BY,
            "data": {
                "industry": industry,
                "employeeCount": initial_employee_count,
            },
        },
        "update_data_template": {
            "businessName": updated_business_name,
            "categories": ["technology", "software", "consulting"],
            "address": {
                "street": fake.street_address(),
                "city": city,
                "state": state,
                "zip": fake.zipcode(),
            },
            "updatedBy": UPDATED_BY,
            "data": {
                "industry": industry,
                "employeeCount": updated_employee_count,
                "founded": founded_year,
            },
        },
    }


def generate_and_load_data(engine: AIMarketingEngine) -> Dict[str, Any]:
    """Create data in priority order and build test fixtures."""
    test_data_updates: Dict[str, Any] = {
        "corporation_profile_test_data": [],
        "corporation_profile_get_test_data": [],
        "corporation_profile_list_test_data": [],
        "corporation_profile_delete_test_data": [],
        "corporation_profile_insert_update_flow_test_data": [],
        "place_test_data": [],
        "place_get_test_data": [],
        "place_list_test_data": [],
        "place_delete_test_data": [],
        "contact_profile_test_data": [],
        "contact_profile_get_test_data": [],
        "contact_profile_list_test_data": [],
        "contact_profile_delete_test_data": [],
        "contact_request_test_data": [],
        "contact_request_get_test_data": [],
        "contact_request_list_test_data": [],
        "contact_request_delete_test_data": [],
        "nested_resolver_test_data": [],
    }

    # 1) CorporationProfile
    corporation_name = fake.company()
    corporation_payload = {
        "externalId": f"EXT-CORP-{fake.random_number(digits=6, fix_len=True)}",
        "corporationType": fake.random_element(["private", "public", "nonprofit"]),
        "businessName": corporation_name,
        "categories": fake.random_elements(
            elements=["technology", "software", "consulting", "finance", "retail"],
            length=2,
            unique=True,
        ),
        "address": {
            "street": fake.street_address(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "zip": fake.zipcode(),
        },
        "data": {
            "industry": fake.random_element(
                ["Technology", "Finance", "Healthcare", "Retail"]
            ),
            "employeeCount": str(fake.random_int(min=50, max=2000)),
        },
        "updatedBy": UPDATED_BY,
    }

    corporation_mutation = """
    mutation InsertUpdateCorporationProfile(
        $corporationUuid: String
        $externalId: String
        $corporationType: String
        $businessName: String
        $categories: [String]
        $address: JSON
        $data: JSON
        $updatedBy: String!
    ) {
        insertUpdateCorporationProfile(
            corporationUuid: $corporationUuid
            externalId: $externalId
            corporationType: $corporationType
            businessName: $businessName
            categories: $categories
            address: $address
            data: $data
            updatedBy: $updatedBy
        ) {
            corporationProfile {
                corporationUuid
                externalId
                corporationType
                businessName
                categories
                address
                data
            }
        }
    }
    """
    corp_result = run_graphql_mutation(
        engine, corporation_mutation, corporation_payload, label="insertUpdateCorporationProfile"
    )

    if not corp_result:
        raise RuntimeError("Failed to create CorporationProfile")

    corp_profile = corp_result["insertUpdateCorporationProfile"]["corporationProfile"]
    corporation_uuid = corp_profile["corporationUuid"]

    test_data_updates["corporation_profile_test_data"].append(
        {**corporation_payload, "corporationUuid": corporation_uuid}
    )
    test_data_updates["corporation_profile_get_test_data"].append(
        {"corporationUuid": corporation_uuid}
    )
    test_data_updates["corporation_profile_list_test_data"].append(
        {"corporationType": corporation_payload["corporationType"], "limit": 10}
    )
    test_data_updates["corporation_profile_delete_test_data"].append(
        {"corporationUuid": str(uuid.uuid4())}  # Keep delete isolated from created data
    )
    test_data_updates["corporation_profile_insert_update_flow_test_data"].append(
        generate_corporation_profile_flow_case()
    )

    # 2) Place (depends on CorporationProfile)
    place_name = fake.company()
    place_payload = {
        # Don't provide placeUuid for INSERT - let backend generate it
        "region": f"{fake.country_code()}-{fake.state_abbr()}",
        "latitude": str(fake.latitude()),
        "longitude": str(fake.longitude()),
        "businessName": place_name,
        "address": fake.address().replace("\n", ", "),
        "phoneNumber": fake.phone_number(),
        "website": fake.url(),
        "types": [fake.random_element(["restaurant", "cafe", "retail", "office"])],
        "corporationUuid": corporation_uuid,
        "updatedBy": UPDATED_BY,
    }

    place_mutation = """
    mutation InsertUpdatePlace(
        $placeUuid: String
        $region: String
        $latitude: String
        $longitude: String
        $businessName: String
        $address: String
        $phoneNumber: String
        $website: String
        $types: [String]
        $corporationUuid: String
        $updatedBy: String!
    ) {
        insertUpdatePlace(
            placeUuid: $placeUuid
            region: $region
            latitude: $latitude
            longitude: $longitude
            businessName: $businessName
            address: $address
            phoneNumber: $phoneNumber
            website: $website
            types: $types
            corporationUuid: $corporationUuid
            updatedBy: $updatedBy
        ) {
            place {
                placeUuid
                region
                latitude
                longitude
                businessName
                address
                phoneNumber
                website
                types
                corporationUuid
            }
        }
    }
    """
    place_result = run_graphql_mutation(
        engine, place_mutation, place_payload, label="insertUpdatePlace"
    )
    if not place_result:
        raise RuntimeError("Failed to create Place")

    place = place_result["insertUpdatePlace"]["place"]
    place_uuid = place["placeUuid"]
    # Ensure payload reflects actual UUID that may be generated/returned by API
    place_payload["placeUuid"] = place_uuid

    test_data_updates["place_test_data"].append(place_payload)
    test_data_updates["place_get_test_data"].append({"placeUuid": place_uuid})
    test_data_updates["place_list_test_data"].append(
        {"region": place_payload["region"], "limit": 10}
    )
    test_data_updates["place_delete_test_data"].append({"placeUuid": str(uuid.uuid4())})

    # 3) ContactProfile (depends on Place)
    contact_email = fake.email()
    contact_payload = {
        # Don't provide contactUuid for INSERT - let backend generate it
        "email": contact_email,
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "placeUuid": place_uuid,
        "updatedBy": UPDATED_BY,
        "data": {
            "phone": fake.phone_number(),
            "department": fake.job(),
        },
    }

    contact_mutation = """
    mutation InsertUpdateContactProfile(
        $placeUuid: String!
        $contactUuid: String
        $email: String
        $endpointId: String
        $firstName: String
        $lastName: String
        $data: JSON
        $updatedBy: String!
    ) {
        insertUpdateContactProfile(
            placeUuid: $placeUuid
            contactUuid: $contactUuid
            email: $email
            endpointId: $endpointId
            firstName: $firstName
            lastName: $lastName
            data: $data
            updatedBy: $updatedBy
        ) {
            contactProfile {
                contactUuid
                email
                placeUuid
                firstName
                lastName
                data
            }
        }
    }
    """
    contact_result = run_graphql_mutation(
        engine,
        contact_mutation,
        {**contact_payload, "endpointId": ENDPOINT_ID},
        label="insertUpdateContactProfile",
    )
    if not contact_result:
        raise RuntimeError("Failed to create ContactProfile")

    contact_profile = contact_result["insertUpdateContactProfile"]["contactProfile"]
    contact_uuid = contact_profile["contactUuid"]
    contact_payload["contactUuid"] = contact_uuid

    test_data_updates["contact_profile_test_data"].append(contact_payload)
    test_data_updates["contact_profile_get_test_data"].append(
        {"contactUuid": contact_uuid}
    )
    test_data_updates["contact_profile_list_test_data"].extend(
        [
            {"limit": 10, "pageNumber": 1},
            {"email": contact_email, "limit": 5},
        ]
    )
    test_data_updates["contact_profile_delete_test_data"].append(
        {"contactUuid": str(uuid.uuid4())}
    )

    # 4) ContactRequest (depends on ContactProfile + Place)
    request_payload = {
        # Don't provide requestUuid for INSERT - let backend generate it
        "contactUuid": contact_uuid,
        "placeUuid": place_uuid,
        "requestTitle": fake.catch_phrase(),
        "requestDetail": fake.text(max_nb_chars=120),
        "updatedBy": UPDATED_BY,
    }

    request_mutation = """
    mutation InsertUpdateContactRequest(
        $contactUuid: String
        $requestUuid: String
        $placeUuid: String
        $requestTitle: String
        $requestDetail: String
        $updatedBy: String!
    ) {
        insertUpdateContactRequest(
            contactUuid: $contactUuid
            requestUuid: $requestUuid
            placeUuid: $placeUuid
            requestTitle: $requestTitle
            requestDetail: $requestDetail
            updatedBy: $updatedBy
        ) {
            contactRequest {
                requestUuid
                contactUuid
                placeUuid
                requestTitle
                requestDetail
            }
        }
    }
    """
    request_result = run_graphql_mutation(
        engine, request_mutation, request_payload, label="insertUpdateContactRequest"
    )
    if not request_result:
        raise RuntimeError("Failed to create ContactRequest")

    contact_request = request_result["insertUpdateContactRequest"]["contactRequest"]
    request_uuid = contact_request["requestUuid"]
    request_payload["requestUuid"] = request_uuid

    test_data_updates["contact_request_test_data"].append(request_payload)
    test_data_updates["contact_request_get_test_data"].append(
        {"contactUuid": contact_uuid, "requestUuid": request_uuid}
    )
    test_data_updates["contact_request_list_test_data"].append(
        {"contactUuid": contact_uuid, "limit": 10}
    )
    test_data_updates["contact_request_delete_test_data"].append(
        {"requestUuid": str(uuid.uuid4())}
    )

    # Nested resolver expectations for 4-level chain
    test_data_updates["nested_resolver_test_data"].append(
        {
            "description": "Test 4-level nesting: ContactRequest -> ContactProfile -> Place -> CorporationProfile",
            "contactUuid": contact_uuid,
            "requestUuid": request_uuid,
            "expectedContactEmail": contact_email,
            "expectedPlaceName": place_name,
            "expectedCorpName": corporation_name,
        }
    )

    return test_data_updates


def main() -> None:
    preview_mode = "--preview" in sys.argv
    engine_instance = create_engine()
    updates = generate_and_load_data(engine_instance)

    # Pretty print JSON for visibility
    json_output = json.dumps(updates, indent=2)
    if preview_mode:
        print("\n" + "=" * 80)
        print("PREVIEW MODE - Data will NOT be saved")
        print("=" * 80)
        print(json_output)
        print("=" * 80)
        return

    persist_test_data(updates)
    print(json_output)
    print("\n--- Data Loading Complete ---")


if __name__ == "__main__":
    main()
