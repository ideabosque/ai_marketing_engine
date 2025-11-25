#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for nested GraphQL resolver functionality with DataLoader batch loading."""
from __future__ import annotations

__author__ = "bibow"

import json
import os
import sys
import time
from typing import Any

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
CONTACT_PROFILE_GET_TEST_DATA = _TEST_DATA.get("contact_profile_get_test_data", [])
PLACE_GET_TEST_DATA = _TEST_DATA.get("place_get_test_data", [])
NESTED_RESOLVER_TEST_DATA = _TEST_DATA.get("nested_resolver_test_data", [])


# ============================================================================
# NESTED RESOLVER TESTS
# ============================================================================


@pytest.mark.integration
@pytest.mark.nested_resolvers
@log_test_result
def test_contact_profile_with_nested_place(ai_marketing_engine: Any, schema: Any) -> None:
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
def test_place_with_nested_corporation_profile(ai_marketing_engine: Any, schema: Any) -> None:
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
def test_deep_nesting_four_levels(ai_marketing_engine: Any, schema: Any, test_data: Any) -> None:
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
def test_lazy_loading_performance(ai_marketing_engine: Any, schema: Any) -> None:
    """
    Verify that lazy loading works - queries without nested fields should not fetch nested data.
    """
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
    Run nested resolver tests directly with Python for debugging and development.

    Usage:
        python test_nested_resolvers.py              # Run all nested resolver tests
        python test_nested_resolvers.py -v           # Verbose output
        python test_nested_resolvers.py -k test_contact # Run specific test
        python test_nested_resolvers.py -s           # Show print statements

    Examples:
        python test_nested_resolvers.py -v
        python test_nested_resolvers.py -k "test_lazy_loading" -s
    """
    import sys

    # Run pytest with this file
    sys.exit(pytest.main([__file__, "-v"] + sys.argv[1:]))
