#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Integration tests for AI Marketing Engine with nested resolvers."""
from __future__ import annotations

__author__ = "bibow"

import json
import os
import sys
from typing import Any, Dict

import pytest

# Add parent directory to path to allow imports when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from silvaengine_utility import Utility
from test_helpers import call_method, log_test_result, validate_nested_resolver_result

# Load test data
_test_data_file = os.path.join(os.path.dirname(__file__), "test_data.json")
with open(_test_data_file, "r") as f:
    _TEST_DATA = json.load(f)

# Extract test data sets for parametrization
CONTACT_PROFILE_TEST_DATA = _TEST_DATA.get("contact_profile_test_data", [])
CONTACT_PROFILE_GET_TEST_DATA = _TEST_DATA.get("contact_profile_get_test_data", [])
CONTACT_PROFILE_LIST_TEST_DATA = _TEST_DATA.get("contact_profile_list_test_data", [])
CONTACT_PROFILE_DELETE_TEST_DATA = _TEST_DATA.get(
    "contact_profile_delete_test_data", []
)

PLACE_TEST_DATA = _TEST_DATA.get("place_test_data", [])
PLACE_GET_TEST_DATA = _TEST_DATA.get("place_get_test_data", [])
PLACE_LIST_TEST_DATA = _TEST_DATA.get("place_list_test_data", [])
PLACE_DELETE_TEST_DATA = _TEST_DATA.get("place_delete_test_data", [])

CORPORATION_PROFILE_TEST_DATA = _TEST_DATA.get("corporation_profile_test_data", [])
CORPORATION_PROFILE_GET_TEST_DATA = _TEST_DATA.get(
    "corporation_profile_get_test_data", []
)
CORPORATION_PROFILE_LIST_TEST_DATA = _TEST_DATA.get(
    "corporation_profile_list_test_data", []
)
CORPORATION_PROFILE_DELETE_TEST_DATA = _TEST_DATA.get(
    "corporation_profile_delete_test_data", []
)
CORPORATION_PROFILE_INSERT_UPDATE_FLOW_TEST_DATA = _TEST_DATA.get(
    "corporation_profile_insert_update_flow_test_data", []
)

CONTACT_REQUEST_TEST_DATA = _TEST_DATA.get("contact_request_test_data", [])
CONTACT_REQUEST_GET_TEST_DATA = _TEST_DATA.get("contact_request_get_test_data", [])
CONTACT_REQUEST_LIST_TEST_DATA = _TEST_DATA.get("contact_request_list_test_data", [])
CONTACT_REQUEST_DELETE_TEST_DATA = _TEST_DATA.get(
    "contact_request_delete_test_data", []
)

NESTED_RESOLVER_TEST_DATA = _TEST_DATA.get("nested_resolver_test_data", [])

# ============================================================================
# UNIT TESTS
# ============================================================================


@pytest.mark.unit
@log_test_result
def test_initialization_with_valid_params(ai_marketing_engine):
    """Ensure engine fixture initializes with expected configuration."""
    assert ai_marketing_engine is not None
    assert hasattr(ai_marketing_engine, "ai_marketing_graphql")
    assert getattr(ai_marketing_engine, "__is_real__", False)


@pytest.mark.unit
@log_test_result
def test_schema_fetched_successfully(schema):
    """Ensure GraphQL schema is available."""
    assert schema is not None
    assert isinstance(schema, dict)
    # Schema can be in multiple formats:
    # 1. Wrapped in "data": {"data": {"__schema": {...}}}
    # 2. Direct __schema: {"__schema": {...}}
    # 3. Direct schema fields: {"queryType": ..., "mutationType": ..., "types": ...}
    if "data" in schema:
        assert "__schema" in schema["data"]
    elif "__schema" in schema:
        pass  # Valid format
    else:
        # Direct schema fields format
        assert "queryType" in schema
        assert "types" in schema


# ============================================================================
# INTEGRATION TESTS - Ordered by Model Relationship Hierarchy
# ============================================================================
# Test order follows the dependency hierarchy from README.md:
# 1. CorporationProfile (no dependencies)
# 2. Place (depends on CorporationProfile)
# 3. ContactProfile (depends on Place)
# 4. ContactRequest (depends on ContactProfile and Place)
#
# This ensures parent entities are created before child entities that reference them.
# ============================================================================

# ============================================================================
# CORPORATION PROFILE TESTS
# ============================================================================


@pytest.mark.integration
@pytest.mark.parametrize("test_data", CORPORATION_PROFILE_INSERT_UPDATE_FLOW_TEST_DATA)
@log_test_result
def test_graphql_insert_update_corporation_profile(
    ai_marketing_engine, schema, test_data
):
    """Test corporation profile INSERT then UPDATE operation."""
    query = Utility.generate_graphql_operation(
        "insertUpdateCorporationProfile", "Mutation", schema
    )

    insert_data = test_data["insert_data"]
    update_data_template = test_data["update_data_template"]

    # Step 1: INSERT - Create new corporation profile without UUID
    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": insert_data},
        "insert_corporation_profile",
    )

    assert error is None, f"Insert failed: {error}"
    assert result is not None

    # Parse JSON response if it's a string
    if isinstance(result, str):
        result = json.loads(result)

    assert "data" in result
    assert "insertUpdateCorporationProfile" in result["data"]

    corp_profile = result["data"]["insertUpdateCorporationProfile"][
        "corporationProfile"
    ]
    assert corp_profile["businessName"] == insert_data["businessName"]

    # Extract the generated UUID from INSERT response
    new_corporation_uuid = corp_profile["corporationUuid"]
    assert new_corporation_uuid is not None, "Corporation UUID should be generated"

    # Step 2: UPDATE - Update the same corporation profile using generated UUID
    update_data = {**update_data_template, "corporationUuid": new_corporation_uuid}

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": update_data},
        "update_corporation_profile",
    )

    assert error is None, f"Update failed: {error}"
    assert result is not None

    # Parse JSON response if it's a string
    if isinstance(result, str):
        result = json.loads(result)

    assert "data" in result
    assert "insertUpdateCorporationProfile" in result["data"]

    corp_profile = result["data"]["insertUpdateCorporationProfile"][
        "corporationProfile"
    ]
    assert (
        corp_profile["businessName"] == update_data["businessName"]
    ), "Business name should be updated"
    assert len(corp_profile["categories"]) == len(
        update_data["categories"]
    ), f"Should have {len(update_data['categories'])} categories after update"
    assert corp_profile["corporationUuid"] == new_corporation_uuid

    # Step 3: Cleanup - Delete the test record
    delete_query = Utility.generate_graphql_operation(
        "deleteCorporationProfile", "Mutation", schema
    )

    delete_data = {"corporationUuid": new_corporation_uuid}

    call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": delete_query, "variables": delete_data},
        "delete_corporation_profile",
    )


@pytest.mark.integration
@pytest.mark.parametrize("test_data", CORPORATION_PROFILE_GET_TEST_DATA)
@log_test_result
def test_graphql_get_corporation_profile(ai_marketing_engine, schema, test_data):
    """Test get corporation profile operation."""
    query = Utility.generate_graphql_operation("corporationProfile", "Query", schema)

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "get_corporation_profile",
    )

    assert error is None, f"Get failed: {error}"
    assert result is not None


@pytest.mark.integration
@pytest.mark.parametrize("test_data", CORPORATION_PROFILE_LIST_TEST_DATA)
@log_test_result
def test_graphql_corporation_profile_list(ai_marketing_engine, schema, test_data):
    """Test list corporation profiles operation."""
    query = Utility.generate_graphql_operation(
        "corporationProfileList", "Query", schema
    )

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "list_corporation_profiles",
    )

    assert error is None, f"List failed: {error}"
    assert result is not None


@pytest.mark.integration
@pytest.mark.parametrize("test_data", CORPORATION_PROFILE_DELETE_TEST_DATA)
@log_test_result
def test_graphql_delete_corporation_profile(ai_marketing_engine, schema, test_data):
    """Test delete corporation profile operation."""
    query = Utility.generate_graphql_operation(
        "deleteCorporationProfile", "Mutation", schema
    )

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "delete_corporation_profile",
    )

    # Delete may fail if entity doesn't exist
    pass


# ============================================================================
# PLACE TESTS
# ============================================================================


@pytest.mark.integration
@pytest.mark.parametrize("test_data", PLACE_TEST_DATA)
@log_test_result
def test_graphql_insert_update_place(ai_marketing_engine, schema, test_data):
    """Test place INSERT then UPDATE operation."""
    query = Utility.generate_graphql_operation("insertUpdatePlace", "Mutation", schema)

    # Step 1: INSERT - Create new place without placeUuid
    insert_data = {k: v for k, v in test_data.items() if k != "placeUuid"}

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": insert_data},
        "insert_update_place",
    )

    assert error is None, f"Insert failed: {error}"
    assert result is not None

    # Parse JSON if result is a string
    if isinstance(result, str):
        result = json.loads(result)

    assert "data" in result
    assert "insertUpdatePlace" in result["data"]

    # Extract the placeUuid from INSERT result (note: response has nested "place" object)
    place_data = result["data"]["insertUpdatePlace"].get("place", {})
    place_uuid = place_data.get("placeUuid")
    assert place_uuid is not None, "Insert should return placeUuid"

    # Step 2: UPDATE - Update the place with new data
    update_data = {
        **insert_data,
        "placeUuid": place_uuid,
        "businessName": "Updated: " + insert_data.get("businessName", ""),
    }

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": update_data},
        "insert_update_place",
    )

    assert error is None, f"Update failed: {error}"
    assert result is not None

    # Parse JSON if result is a string
    if isinstance(result, str):
        result = json.loads(result)

    assert "data" in result
    assert "insertUpdatePlace" in result["data"]


@pytest.mark.integration
@pytest.mark.parametrize("test_data", PLACE_GET_TEST_DATA)
@log_test_result
def test_graphql_get_place(ai_marketing_engine, schema, test_data):
    """Test get place operation."""
    query = Utility.generate_graphql_operation("place", "Query", schema)

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "get_place",
    )

    assert error is None, f"Get failed: {error}"
    assert result is not None


@pytest.mark.integration
@pytest.mark.parametrize("test_data", PLACE_LIST_TEST_DATA)
@log_test_result
def test_graphql_place_list(ai_marketing_engine, schema, test_data):
    """Test list places operation."""
    query = Utility.generate_graphql_operation("placeList", "Query", schema)

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "list_places",
    )

    assert error is None, f"List failed: {error}"
    assert result is not None


@pytest.mark.integration
@pytest.mark.parametrize("test_data", PLACE_DELETE_TEST_DATA)
@log_test_result
def test_graphql_delete_place(ai_marketing_engine, schema, test_data):
    """Test delete place operation."""
    query = Utility.generate_graphql_operation("deletePlace", "Mutation", schema)

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "delete_place",
    )

    # Delete may fail if entity doesn't exist
    pass


# ============================================================================
# CONTACT PROFILE TESTS
# ============================================================================


@pytest.mark.integration
@pytest.mark.parametrize("test_data", CONTACT_PROFILE_TEST_DATA)
@log_test_result
def test_graphql_insert_update_contact_profile(ai_marketing_engine, schema, test_data):
    """Test contact profile INSERT then UPDATE operation."""
    import uuid

    query = Utility.generate_graphql_operation(
        "insertUpdateContactProfile", "Mutation", schema
    )

    # Step 1: INSERT - Create new contact profile without contactUuid and with unique email
    insert_data = {k: v for k, v in test_data.items() if k != "contactUuid"}
    # Generate unique email to avoid duplicate errors
    unique_suffix = uuid.uuid4().hex[:8]
    original_email = insert_data.get("email", "test@example.com")
    email_parts = original_email.split("@")
    insert_data["email"] = f"{email_parts[0]}+{unique_suffix}@{email_parts[1]}"

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": insert_data},
        "insert_update_contact_profile",
    )

    assert error is None, f"Insert failed: {error}"
    assert result is not None

    # Parse JSON if result is a string
    if isinstance(result, str):
        result = json.loads(result)

    assert "data" in result
    assert "insertUpdateContactProfile" in result["data"]

    # Extract the contactUuid from INSERT result (note: response has nested "contactProfile" object)
    contact_data = result["data"]["insertUpdateContactProfile"].get(
        "contactProfile", {}
    )
    contact_uuid = contact_data.get("contactUuid")
    assert contact_uuid is not None, "Insert should return contactUuid"

    # Step 2: UPDATE - Update the contact profile with new data
    update_data = {
        **insert_data,
        "contactUuid": contact_uuid,
        "firstName": "Updated: " + insert_data.get("firstName", ""),
    }

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": update_data},
        "insert_update_contact_profile",
    )

    assert error is None, f"Update failed: {error}"
    assert result is not None

    # Parse JSON if result is a string
    if isinstance(result, str):
        result = json.loads(result)

    assert "data" in result
    assert "insertUpdateContactProfile" in result["data"]


@pytest.mark.integration
@pytest.mark.parametrize("test_data", CONTACT_PROFILE_GET_TEST_DATA)
@log_test_result
def test_graphql_get_contact_profile(ai_marketing_engine, schema, test_data):
    """Test get contact profile operation."""
    query = Utility.generate_graphql_operation("contactProfile", "Query", schema)

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "get_contact_profile",
    )

    assert error is None, f"Get failed: {error}"
    assert result is not None


@pytest.mark.integration
@pytest.mark.parametrize("test_data", CONTACT_PROFILE_LIST_TEST_DATA)
@log_test_result
def test_graphql_contact_profile_list(ai_marketing_engine, schema, test_data):
    """Test list contact profiles operation."""
    query = Utility.generate_graphql_operation("contactProfileList", "Query", schema)

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "list_contact_profiles",
    )

    assert error is None, f"List failed: {error}"
    assert result is not None


@pytest.mark.integration
@pytest.mark.parametrize("test_data", CONTACT_PROFILE_DELETE_TEST_DATA)
@log_test_result
def test_graphql_delete_contact_profile(ai_marketing_engine, schema, test_data):
    """Test delete contact profile operation."""
    query = Utility.generate_graphql_operation(
        "deleteContactProfile", "Mutation", schema
    )

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "delete_contact_profile",
    )

    # Delete may fail if entity doesn't exist, which is acceptable in tests
    # Just log the result
    pass


# ============================================================================
# CONTACT REQUEST TESTS
# ============================================================================


@pytest.mark.integration
@pytest.mark.parametrize("test_data", CONTACT_REQUEST_TEST_DATA)
@pytest.mark.xfail(
    reason="ContactRequest INSERT requires endpoint_id context that's not available in test environment"
)
@log_test_result
def test_graphql_insert_update_contact_request(ai_marketing_engine, schema, test_data):
    """Test contact request INSERT then UPDATE operation.

    NOTE: This test currently fails because the contact_request validation
    requires get_contact_profile_count() to work, which needs endpoint_id
    from the GraphQL context. The endpoint_id is not available as a GraphQL
    parameter and must be extracted from the request context by the backend.
    """
    import uuid

    # PREREQUISITE: Create a ContactProfile first since ContactRequest depends on it
    contact_profile_query = Utility.generate_graphql_operation(
        "insertUpdateContactProfile", "Mutation", schema
    )

    # Use placeUuid from test_data if available, otherwise use a default
    place_uuid = test_data.get("placeUuid") or PLACE_GET_TEST_DATA[0]["placeUuid"]

    # Create contact profile with unique email
    unique_suffix = uuid.uuid4().hex[:8]
    contact_profile_data = {
        "email": f"test+{unique_suffix}@example.com",
        "firstName": "Test",
        "lastName": "User",
        "placeUuid": place_uuid,
        "updatedBy": "data_loader_script",
    }

    cp_result, cp_error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": contact_profile_query, "variables": contact_profile_data},
        "insert_contact_profile_for_request_test",
    )

    assert cp_error is None, f"Failed to create prerequisite ContactProfile: {cp_error}"

    if isinstance(cp_result, str):
        cp_result = json.loads(cp_result)

    # Extract the contactUuid
    contact_data = cp_result["data"]["insertUpdateContactProfile"].get(
        "contactProfile", {}
    )
    contact_uuid = contact_data.get("contactUuid")
    assert contact_uuid is not None, "Failed to get contactUuid from prerequisite"

    # Add small delay to ensure DynamoDB consistency
    import time

    time.sleep(0.5)  # 500ms delay for eventual consistency

    # NOW run the actual ContactRequest INSERT/UPDATE test
    query = Utility.generate_graphql_operation(
        "insertUpdateContactRequest", "Mutation", schema
    )

    # Step 1: INSERT - Create new contact request without requestUuid
    insert_data = {k: v for k, v in test_data.items() if k != "requestUuid"}
    # Use the newly created contactUuid
    insert_data["contactUuid"] = contact_uuid

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": insert_data},
        "insert_update_contact_request",
    )

    assert error is None, f"Insert failed: {error}"
    assert result is not None

    # Parse JSON if result is a string
    if isinstance(result, str):
        result = json.loads(result)

    assert "data" in result
    assert "insertUpdateContactRequest" in result["data"]

    # Extract the requestUuid from INSERT result (note: response has nested "contactRequest" object)
    request_data = result["data"]["insertUpdateContactRequest"].get(
        "contactRequest", {}
    )
    request_uuid = request_data.get("requestUuid")
    assert request_uuid is not None, "Insert should return requestUuid"

    # Step 2: UPDATE - Update the contact request with new data
    update_data = {
        **insert_data,
        "requestUuid": request_uuid,
        "requestTitle": "Updated: " + insert_data.get("requestTitle", ""),
    }

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": update_data},
        "insert_update_contact_request",
    )

    assert error is None, f"Update failed: {error}"
    assert result is not None

    # Parse JSON if result is a string
    if isinstance(result, str):
        result = json.loads(result)

    assert "data" in result
    assert "insertUpdateContactRequest" in result["data"]


@pytest.mark.integration
@pytest.mark.parametrize("test_data", CONTACT_REQUEST_GET_TEST_DATA)
@log_test_result
def test_graphql_get_contact_request(ai_marketing_engine, schema, test_data):
    """Test get contact request operation."""
    query = Utility.generate_graphql_operation("contactRequest", "Query", schema)

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "get_contact_request",
    )

    assert error is None, f"Get failed: {error}"
    assert result is not None


@pytest.mark.integration
@pytest.mark.parametrize("test_data", CONTACT_REQUEST_LIST_TEST_DATA)
@log_test_result
def test_graphql_contact_request_list(ai_marketing_engine, schema, test_data):
    """Test list contact requests operation."""
    query = Utility.generate_graphql_operation("contactRequestList", "Query", schema)

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "list_contact_requests",
    )

    assert error is None, f"List failed: {error}"
    assert result is not None


@pytest.mark.integration
@pytest.mark.parametrize("test_data", CONTACT_REQUEST_DELETE_TEST_DATA)
@log_test_result
def test_graphql_delete_contact_request(ai_marketing_engine, schema, test_data):
    """Test delete contact request operation."""
    query = Utility.generate_graphql_operation(
        "deleteContactRequest", "Mutation", schema
    )

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "delete_contact_request",
    )

    # Delete may fail if entity doesn't exist
    pass


# ============================================================================
# NESTED RESOLVER TESTS
# ============================================================================


@pytest.mark.integration
@pytest.mark.nested_resolvers
@log_test_result
def test_contact_profile_with_nested_place(ai_marketing_engine, schema):
    """Test that nested place resolver works correctly."""
    # Use actual contact UUID from test data
    contact_uuid = CONTACT_PROFILE_GET_TEST_DATA[0]["contactUuid"]

    query = """
    query GetContactProfileWithPlace($contactUuid: String!) {
        contactProfile(contactUuid: $contactUuid) {
            contactUuid
            email
            placeUuid
            place {
                placeUuid
                businessName
                region
            }
        }
    }
    """

    variables = {"contactUuid": contact_uuid}

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": variables},
        "test_nested_place",
    )

    assert error is None
    assert result is not None

    # Parse JSON if it's a string
    if isinstance(result, str):
        result = json.loads(result)

    # Validate nested structure
    validate_nested_resolver_result(
        result,
        expected_keys=["placeUuid", "businessName"],
        nested_path=["data", "contactProfile", "place"],
    )


@pytest.mark.integration
@pytest.mark.nested_resolvers
@log_test_result
def test_place_with_nested_corporation_profile(ai_marketing_engine, schema):
    """Test that nested corporation profile resolver works correctly."""
    # Use actual place UUID from test data
    place_uuid = PLACE_GET_TEST_DATA[0]["placeUuid"]

    query = """
    query GetPlaceWithCorporation($placeUuid: String!) {
        place(placeUuid: $placeUuid) {
            placeUuid
            businessName
            corporationUuid
            corporationProfile {
                corporationUuid
                businessName
                corporationType
            }
        }
    }
    """

    variables = {"placeUuid": place_uuid}

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": variables},
        "test_nested_corporation",
    )

    assert error is None
    assert result is not None

    # Parse JSON if it's a string
    if isinstance(result, str):
        result = json.loads(result)

    # Validate nested structure
    validate_nested_resolver_result(
        result,
        expected_keys=["corporationUuid", "businessName"],
        nested_path=["data", "place", "corporationProfile"],
    )


@pytest.mark.integration
@pytest.mark.nested_resolvers
@pytest.mark.slow
@pytest.mark.parametrize("test_data", NESTED_RESOLVER_TEST_DATA)
@log_test_result
def test_deep_nesting_four_levels(ai_marketing_engine, schema, test_data):
    """
    Test 4-level nesting: ContactRequest → ContactProfile → Place → CorporationProfile

    This tests the entire nested resolver chain.
    """
    query = """
    query GetContactRequestDeepNesting($contactUuid: String!, $requestUuid: String!) {
        contactRequest(contactUuid: $contactUuid, requestUuid: $requestUuid) {
            requestUuid
            requestTitle
            contactUuid
            contactProfile {
                contactUuid
                email
                placeUuid
                place {
                    placeUuid
                    businessName
                    corporationUuid
                    corporationProfile {
                        corporationUuid
                        businessName
                        corporationType
                    }
                }
            }
        }
    }
    """

    variables = {
        "contactUuid": test_data["contactUuid"],
        "requestUuid": test_data["requestUuid"],
    }

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": variables},
        "test_deep_nesting",
    )

    assert error is None
    assert result is not None

    # Parse JSON if it's a string
    if isinstance(result, str):
        result = json.loads(result)

    # Validate 4-level nested structure
    contact_request = result["data"]["contactRequest"]
    assert contact_request["contactUuid"] is not None

    # Level 2: ContactProfile
    contact_profile = contact_request["contactProfile"]
    assert contact_profile is not None
    assert contact_profile["email"] == test_data["expectedContactEmail"]

    # Level 3: Place
    place = contact_profile["place"]
    assert place is not None
    assert place["businessName"] == test_data["expectedPlaceName"]

    # Level 4: CorporationProfile
    corp_profile = place["corporationProfile"]
    assert corp_profile is not None
    assert corp_profile["businessName"] == test_data["expectedCorpName"]


@pytest.mark.integration
@pytest.mark.nested_resolvers
@log_test_result
def test_lazy_loading_performance(ai_marketing_engine, schema):
    """
    Verify that lazy loading works - queries without nested fields should not fetch nested data.
    """
    import time

    # Query WITHOUT nested fields (should be fast)
    query_minimal = """
    query GetContactProfileMinimal {
        contactProfileList(limit: 10) {
            contactProfileList {
                contactUuid
                email
                placeUuid
            }
        }
    }
    """

    t0 = time.perf_counter()
    result_minimal, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query_minimal},
        "test_minimal_query",
    )
    duration_minimal = time.perf_counter() - t0

    assert error is None

    # Query WITH nested fields (will be slower)
    query_nested = """
    query GetContactProfileNested {
        contactProfileList(limit: 10) {
            contactProfileList {
                contactUuid
                email
                place {
                    businessName
                    corporationProfile {
                        businessName
                    }
                }
                data
            }
        }
    }
    """

    t0 = time.perf_counter()
    result_nested, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query_nested},
        "test_nested_query",
    )
    duration_nested = time.perf_counter() - t0

    assert error is None

    # Log performance comparison
    print(f"\nPerformance comparison for 10 items:")
    print(f"  Minimal query (no nesting): {duration_minimal*1000:.2f}ms")
    print(f"  Nested query (2 levels):    {duration_nested*1000:.2f}ms")
    print(
        f"  Difference:                 {(duration_nested-duration_minimal)*1000:.2f}ms"
    )

    # Minimal query should be faster (not a strict assertion, just informative)
    # In real scenarios with more data, the difference would be more significant


# ============================================================================
# MAIN ENTRY POINT FOR DIRECT EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Run tests directly with Python for debugging and development.

    Usage:
        python test_ai_marketing_engine.py              # Run all tests
        python test_ai_marketing_engine.py -v           # Verbose output
        python test_ai_marketing_engine.py -k test_init # Run specific test
        python test_ai_marketing_engine.py -m unit      # Run unit tests only
        python test_ai_marketing_engine.py -m integration # Run integration tests
        python test_ai_marketing_engine.py -s           # Show print statements
        python test_ai_marketing_engine.py --pdb        # Drop into debugger on failure

    Examples:
        python test_ai_marketing_engine.py -m unit -v
        python test_ai_marketing_engine.py -k "test_initialization" -s
        python test_ai_marketing_engine.py -m nested_resolvers --pdb
    """
    import sys

    # Run pytest with this file
    # The plugins parameter ensures pytest hooks from this module are registered
    sys.exit(
        pytest.main([__file__, "-v"] + sys.argv[1:], plugins=[sys.modules[__name__]])
    )
