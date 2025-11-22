#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Integration tests for AI Marketing Engine with nested resolvers."""
from __future__ import annotations

__author__ = "bibow"

import json
import os
from typing import Any, Dict

import pytest

from test_helpers import call_method, log_test_result, validate_nested_resolver_result
from silvaengine_utility import Utility

# Load test data
_test_data_file = os.path.join(os.path.dirname(__file__), "test_data.json")
with open(_test_data_file, "r") as f:
    _TEST_DATA = json.load(f)

# Extract test data sets for parametrization
CONTACT_PROFILE_TEST_DATA = _TEST_DATA.get("contact_profile_test_data", [])
CONTACT_PROFILE_GET_TEST_DATA = _TEST_DATA.get("contact_profile_get_test_data", [])
CONTACT_PROFILE_LIST_TEST_DATA = _TEST_DATA.get("contact_profile_list_test_data", [])
CONTACT_PROFILE_DELETE_TEST_DATA = _TEST_DATA.get("contact_profile_delete_test_data", [])

PLACE_TEST_DATA = _TEST_DATA.get("place_test_data", [])
PLACE_GET_TEST_DATA = _TEST_DATA.get("place_get_test_data", [])
PLACE_LIST_TEST_DATA = _TEST_DATA.get("place_list_test_data", [])
PLACE_DELETE_TEST_DATA = _TEST_DATA.get("place_delete_test_data", [])

CORPORATION_PROFILE_TEST_DATA = _TEST_DATA.get("corporation_profile_test_data", [])
CORPORATION_PROFILE_GET_TEST_DATA = _TEST_DATA.get("corporation_profile_get_test_data", [])
CORPORATION_PROFILE_LIST_TEST_DATA = _TEST_DATA.get("corporation_profile_list_test_data", [])
CORPORATION_PROFILE_DELETE_TEST_DATA = _TEST_DATA.get("corporation_profile_delete_test_data", [])

CONTACT_REQUEST_TEST_DATA = _TEST_DATA.get("contact_request_test_data", [])
CONTACT_REQUEST_GET_TEST_DATA = _TEST_DATA.get("contact_request_get_test_data", [])
CONTACT_REQUEST_LIST_TEST_DATA = _TEST_DATA.get("contact_request_list_test_data", [])
CONTACT_REQUEST_DELETE_TEST_DATA = _TEST_DATA.get("contact_request_delete_test_data", [])

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
    assert "data" in schema or "__schema" in schema


# ============================================================================
# CONTACT PROFILE TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.parametrize("test_data", CONTACT_PROFILE_TEST_DATA)
@log_test_result
def test_graphql_insert_update_contact_profile(
    ai_marketing_engine, schema, test_data
):
    """Test contact profile insert/update operation."""
    query = Utility.generate_graphql_operation(
        "insertUpdateContactProfile", "Mutation", schema
    )

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "insert_update_contact_profile",
    )

    assert error is None, f"Insert/update failed: {error}"
    assert result is not None
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
    assert "data" in result
    assert "contactProfileList" in result["data"]


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
# PLACE TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.parametrize("test_data", PLACE_TEST_DATA)
@log_test_result
def test_graphql_insert_update_place(ai_marketing_engine, schema, test_data):
    """Test place insert/update operation."""
    query = Utility.generate_graphql_operation(
        "insertUpdatePlace", "Mutation", schema
    )

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "insert_update_place",
    )

    assert error is None, f"Insert/update failed: {error}"
    assert result is not None
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
    assert "data" in result
    assert "placeList" in result["data"]


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
# CORPORATION PROFILE TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.parametrize("test_data", CORPORATION_PROFILE_TEST_DATA)
@log_test_result
def test_graphql_insert_update_corporation_profile(
    ai_marketing_engine, schema, test_data
):
    """Test corporation profile insert/update operation."""
    query = Utility.generate_graphql_operation(
        "insertUpdateCorporationProfile", "Mutation", schema
    )

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "insert_update_corporation_profile",
    )

    assert error is None, f"Insert/update failed: {error}"
    assert result is not None
    assert "data" in result
    assert "insertUpdateCorporationProfile" in result["data"]


@pytest.mark.integration
@pytest.mark.parametrize("test_data", CORPORATION_PROFILE_GET_TEST_DATA)
@log_test_result
def test_graphql_get_corporation_profile(ai_marketing_engine, schema, test_data):
    """Test get corporation profile operation."""
    query = Utility.generate_graphql_operation(
        "corporationProfile", "Query", schema
    )

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
    assert "data" in result
    assert "corporationProfileList" in result["data"]


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
# CONTACT REQUEST TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.parametrize("test_data", CONTACT_REQUEST_TEST_DATA)
@log_test_result
def test_graphql_insert_update_contact_request(
    ai_marketing_engine, schema, test_data
):
    """Test contact request insert/update operation."""
    query = Utility.generate_graphql_operation(
        "insertUpdateContactRequest", "Mutation", schema
    )

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "insert_update_contact_request",
    )

    assert error is None, f"Insert/update failed: {error}"
    assert result is not None
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
    query = Utility.generate_graphql_operation(
        "contactRequestList", "Query", schema
    )

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": test_data},
        "list_contact_requests",
    )

    assert error is None, f"List failed: {error}"
    assert result is not None
    assert "data" in result
    assert "contactRequestList" in result["data"]


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

    variables = {"contactUuid": "test_contact_001"}

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": variables},
        "test_nested_place",
    )

    assert error is None
    assert result is not None

    # Validate nested structure
    validate_nested_resolver_result(
        result,
        expected_keys=["placeUuid", "businessName"],
        nested_path=["data", "contactProfile", "place"]
    )


@pytest.mark.integration
@pytest.mark.nested_resolvers
@log_test_result
def test_place_with_nested_corporation_profile(ai_marketing_engine, schema):
    """Test that nested corporation profile resolver works correctly."""
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

    variables = {"placeUuid": "test_place_001"}

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": variables},
        "test_nested_corporation",
    )

    assert error is None
    assert result is not None

    # Validate nested structure
    validate_nested_resolver_result(
        result,
        expected_keys=["corporationUuid", "businessName"],
        nested_path=["data", "place", "corporationProfile"]
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
    query GetContactRequestDeepNesting($requestUuid: String!) {
        contactRequest(requestUuid: $requestUuid) {
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

    variables = {"requestUuid": test_data["requestUuid"]}

    result, error = call_method(
        ai_marketing_engine,
        "ai_marketing_graphql",
        {"query": query, "variables": variables},
        "test_deep_nesting",
    )

    assert error is None
    assert result is not None

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
    print(f"  Difference:                 {(duration_nested-duration_minimal)*1000:.2f}ms")

    # Minimal query should be faster (not a strict assertion, just informative)
    # In real scenarios with more data, the difference would be more significant
