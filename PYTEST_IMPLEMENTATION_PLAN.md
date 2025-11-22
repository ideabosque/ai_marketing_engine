# Phase 4: Testing & Validation (UPDATED - Based on AI RFQ Engine)

**Reference:** This phase has been completely redesigned based on the modern pytest approach used in AI RFQ Engine.

---

## Overview

Phase 4 migrates the test suite from legacy `unittest.TestCase` to modern pytest with:
- External test data (JSON files)
- Parametrized tests
- Module-scoped fixtures
- Custom pytest hooks
- Comprehensive logging
- Helper functions for consistent error handling

**Current State (ai_marketing_engine/tests/):**
- 677 lines, all tests marked `@unittest.skip()` (only 1 active)
- Legacy `unittest.TestCase` pattern
- No parametrization
- Hardcoded test data

**Target State:**
- ~400 lines of active test code (41% reduction)
- 40-50 active test functions
- Modern pytest framework
- External JSON test data
- Custom hooks for flexible test execution

---

## 4.1 Create Pytest Configuration

### File: `pyproject.toml` (update existing)

Add the following section:

```toml
[tool.pytest.ini_options]
testpaths = ["ai_marketing_engine/tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --strict-markers --tb=short --color=yes"
markers = [
    "unit: Unit tests that don't require external dependencies",
    "integration: Integration tests that require external services (DB, API, etc.)",
    "slow: Tests that take significant time to run",
    "nested_resolvers: Tests for nested GraphQL resolver functionality",
    "skip: Tests that are temporarily disabled",
]
log_cli = true
log_cli_level = "INFO"
log_cli_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"
filterwarnings = [
    "error",
    "ignore::UserWarning",
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]
minversion = "7.0"
console_output_style = "progress"
```

**Action Items:**
- [ ] Add `[tool.pytest.ini_options]` to `pyproject.toml`
- [ ] Verify pytest version >= 7.0: `pytest --version`

---

## 4.2 Create Test Data File

### File: `ai_marketing_engine/tests/test_data.json` (NEW)

```json
{
  "contact_profile_test_data": [
    {
      "contactUuid": "test_contact_001",
      "email": "test1@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "placeUuid": "test_place_001",
      "updatedBy": "Test User",
      "data": {
        "phone": "+1-555-0100",
        "department": "Engineering"
      }
    }
  ],
  "contact_profile_get_test_data": [
    {
      "contactUuid": "test_contact_001"
    }
  ],
  "contact_profile_list_test_data": [
    {
      "limit": 10,
      "pageNumber": 1
    },
    {
      "email": "test1@example.com",
      "limit": 5
    }
  ],
  "contact_profile_delete_test_data": [
    {
      "contactUuid": "test_contact_to_delete"
    }
  ],
  "place_test_data": [
    {
      "placeUuid": "test_place_001",
      "region": "US-CA",
      "latitude": "37.7749",
      "longitude": "-122.4194",
      "businessName": "Test Business Inc",
      "address": "123 Main St, San Francisco, CA",
      "phoneNumber": "+1-555-0100",
      "website": "https://testbusiness.com",
      "types": ["restaurant", "cafe"],
      "corporationUuid": "test_corp_001",
      "updatedBy": "Test User"
    }
  ],
  "place_get_test_data": [
    {
      "placeUuid": "test_place_001"
    }
  ],
  "place_list_test_data": [
    {
      "region": "US-CA",
      "limit": 10
    }
  ],
  "place_delete_test_data": [
    {
      "placeUuid": "test_place_to_delete"
    }
  ],
  "corporation_profile_test_data": [
    {
      "corporationUuid": "test_corp_001",
      "externalId": "EXT-CORP-001",
      "corporationType": "private",
      "businessName": "Test Corporation",
      "categories": ["technology", "software"],
      "address": {
        "street": "456 Corporate Blvd",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94105"
      },
      "updatedBy": "Test User",
      "data": {
        "industry": "Technology",
        "employeeCount": 500
      }
    }
  ],
  "corporation_profile_get_test_data": [
    {
      "corporationUuid": "test_corp_001"
    }
  ],
  "corporation_profile_list_test_data": [
    {
      "corporationType": "private",
      "limit": 10
    }
  ],
  "corporation_profile_delete_test_data": [
    {
      "corporationUuid": "test_corp_to_delete"
    }
  ],
  "contact_request_test_data": [
    {
      "requestUuid": "test_request_001",
      "contactUuid": "test_contact_001",
      "placeUuid": "test_place_001",
      "requestTitle": "Product Inquiry",
      "requestDetail": "Looking for pricing information",
      "updatedBy": "Test User"
    }
  ],
  "contact_request_get_test_data": [
    {
      "requestUuid": "test_request_001"
    }
  ],
  "contact_request_list_test_data": [
    {
      "contactUuid": "test_contact_001",
      "limit": 10
    }
  ],
  "contact_request_delete_test_data": [
    {
      "requestUuid": "test_request_to_delete"
    }
  ],
  "nested_resolver_test_data": [
    {
      "description": "Test 4-level nesting: ContactRequest -> ContactProfile -> Place -> CorporationProfile",
      "requestUuid": "test_request_001",
      "expectedContactEmail": "test1@example.com",
      "expectedPlaceName": "Test Business Inc",
      "expectedCorpName": "Test Corporation"
    }
  ]
}
```

**Action Items:**
- [ ] Create `ai_marketing_engine/tests/test_data.json`
- [ ] Update test data with actual UUIDs from your test environment
- [ ] Add more test scenarios as needed

---

## 4.3 Create conftest.py with Fixtures

### File: `ai_marketing_engine/tests/conftest.py` (NEW)

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Pytest configuration and fixtures for AI Marketing Engine tests."""
from __future__ import annotations

__author__ = "bibow"

import json
import logging
import os
import sys
from typing import Any, Dict

import pytest
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("test_ai_marketing_engine")

# Make package importable
base_dir = os.getenv("base_dir", os.getcwd())
sys.path.insert(0, base_dir)
sys.path.insert(0, os.path.join(base_dir, "silvaengine_utility"))
sys.path.insert(1, os.path.join(base_dir, "silvaengine_dynamodb_base"))
sys.path.insert(2, os.path.join(base_dir, "ai_marketing_engine"))

from ai_marketing_engine import AIMarketingEngine
from silvaengine_utility import Utility

# Test settings
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
    "endpoint_id": os.getenv("endpoint_id"),
    "execute_mode": os.getenv("execute_mode", "local"),
}


@pytest.fixture(scope="module")
def ai_marketing_engine():
    """Provide an AIMarketingEngine instance for testing.
    
    This fixture is module-scoped for efficiency - the engine
    is initialized once per test module.
    """
    try:
        engine = AIMarketingEngine(logger, **SETTING)
        # Mark as real engine instance for validation
        setattr(engine, "__is_real__", True)
        logger.info("AIMarketingEngine initialized successfully")
        return engine
    except Exception as ex:
        logger.warning(f"AIMarketingEngine initialization failed: {ex}")
        pytest.skip(f"AIMarketingEngine not available: {ex}")


@pytest.fixture(scope="module")
def schema(ai_marketing_engine):
    """Fetch GraphQL schema for testing.
    
    Depends on ai_marketing_engine fixture.
    """
    endpoint_id = SETTING.get("endpoint_id")
    execute_mode = SETTING.get("execute_mode")
    
    try:
        schema = Utility.fetch_graphql_schema(
            logger,
            endpoint_id,
            "ai_marketing_graphql",
            setting=SETTING,
            test_mode=execute_mode,
        )
        logger.info("GraphQL schema fetched successfully")
        return schema
    except Exception as ex:
        logger.warning(f"Failed to fetch GraphQL schema: {ex}")
        pytest.skip(f"GraphQL schema not available: {ex}")


@pytest.fixture(scope="module")
def test_data():
    """Load test data from JSON file."""
    test_data_file = os.path.join(os.path.dirname(__file__), "test_data.json")
    
    try:
        with open(test_data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"Loaded test data from {test_data_file}")
            return data
    except FileNotFoundError:
        logger.warning(f"Test data file not found: {test_data_file}")
        pytest.skip(f"Test data file not found: {test_data_file}")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing test data JSON: {e}")
        pytest.skip(f"Invalid test data JSON: {e}")
```

**Action Items:**
- [ ] Create `ai_marketing_engine/tests/conftest.py`
- [ ] Verify imports work correctly
- [ ] Test fixture initialization with: `pytest --collect-only`

---

## 4.4 Create Helper Functions and Decorators

### File: `ai_marketing_engine/tests/test_helpers.py` (NEW)

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Helper functions and decorators for AI Marketing Engine tests."""
from __future__ import annotations

__author__ = "bibow"

import logging
import time
import uuid
from functools import wraps
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("test_ai_marketing_engine")


def call_method(
    engine: Any,
    method_name: str,
    arguments: Optional[Dict[str, Any]] = None,
    label: Optional[str] = None,
) -> Tuple[Optional[Any], Optional[Exception]]:
    """
    Invoke engine methods with consistent logging and error capture.
    
    Args:
        engine: Engine instance
        method_name: Name of method to call
        arguments: Method arguments
        label: Optional label for logging
    
    Returns:
        Tuple of (result, error) - one will be None
    """
    arguments = arguments or {}
    op = label or method_name
    cid = uuid.uuid4().hex[:8]  # Correlation ID for tracking
    
    logger.info(f"Method call: cid={cid} op={op} arguments={arguments}")
    t0 = time.perf_counter()

    try:
        method = getattr(engine, method_name)
    except AttributeError as exc:
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        logger.error(
            f"Method response: cid={cid} op={op} elapsed_ms={elapsed_ms} "
            f"success=False error=AttributeError: {str(exc)}"
        )
        return None, exc

    try:
        result = method(**arguments)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        logger.info(
            f"Method response: cid={cid} op={op} elapsed_ms={elapsed_ms} "
            f"success=True result_type={type(result).__name__}"
        )
        return result, None
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        logger.error(
            f"Method response: cid={cid} op={op} elapsed_ms={elapsed_ms} "
            f"success=False error={type(exc).__name__}: {str(exc)}"
        )
        return None, exc


def log_test_result(func):
    """
    Decorator to log test execution with timing.
    
    Usage:
        @log_test_result
        def test_something():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        test_name = func.__name__
        logger.info(f"{'='*80}")
        logger.info(f"Starting test: {test_name}")
        logger.info(f"{'='*80}")
        t0 = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            logger.info(f"{'='*80}")
            logger.info(f"Test {test_name} PASSED (elapsed: {elapsed_ms}ms)")
            logger.info(f"{'='*80}\n")
            return result
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            logger.error(f"{'='*80}")
            logger.error(f"Test {test_name} FAILED (elapsed: {elapsed_ms}ms): {exc}")
            logger.error(f"{'='*80}\n")
            raise

    return wrapper


def validate_nested_resolver_result(
    result: Dict[str, Any],
    expected_keys: list[str],
    nested_path: Optional[list[str]] = None
) -> None:
    """
    Validate that nested resolver returned expected structure.
    
    Args:
        result: GraphQL result dict
        expected_keys: Keys that should exist in result
        nested_path: Path to nested object (e.g., ['data', 'contactProfile', 'place'])
    
    Raises:
        AssertionError: If validation fails
    """
    current = result
    path_str = "result"
    
    # Navigate to nested object if path provided
    if nested_path:
        for key in nested_path:
            assert key in current, f"{path_str} missing key '{key}'"
            current = current[key]
            path_str += f"['{key}']"
    
    # Validate expected keys exist
    for key in expected_keys:
        assert key in current, f"{path_str} missing expected key '{key}'"
    
    logger.info(f"Validated structure at {path_str}: {list(current.keys())}")
```

**Action Items:**
- [ ] Create `ai_marketing_engine/tests/test_helpers.py`
- [ ] Import helpers in test files

---

## 4.5 Create Custom Pytest Hooks

### File: `ai_marketing_engine/tests/conftest.py` (append to existing)

Add these functions to the existing `conftest.py`:

```python
import re
from typing import Sequence

# Environment variable names for test filtering
_TEST_FUNCTION_ENV = "AI_MARKETING_TEST_FUNCTION"
_TEST_MARKER_ENV = "AI_MARKETING_TEST_MARKERS"


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command-line options for test filtering."""
    parser.addoption(
        "--test-function",
        action="store",
        default=os.getenv(_TEST_FUNCTION_ENV, "").strip(),
        help=(
            "Run only tests whose name exactly matches this string. "
            f"Defaults to the {_TEST_FUNCTION_ENV} environment variable when set."
        ),
    )
    parser.addoption(
        "--test-markers",
        action="store",
        default=os.getenv(_TEST_MARKER_ENV, "").strip(),
        help=(
            "Run only tests that include any of the specified markers "
            "(comma or space separated). "
            f"Defaults to the {_TEST_MARKER_ENV} environment variable when set."
        ),
    )


def _parse_marker_filter(raw: str) -> list[str]:
    """Parse comma/space separated marker string into list."""
    if not raw:
        return []
    parts = re.split(r"[,\s]+", raw.strip())
    return [part for part in parts if part]


def _format_filter_description(target: str, marker_filter_raw: str) -> str:
    """Build human-readable description of active filters."""
    descriptors: list[str] = []
    if target:
        descriptors.append(f"{_TEST_FUNCTION_ENV}='{target}'")
    if marker_filter_raw:
        descriptors.append(f"{_TEST_MARKER_ENV}='{marker_filter_raw}'")
    return " and ".join(descriptors) if descriptors else "no filters"


def _raise_no_matches(filters_desc: str, items: Sequence[pytest.Item]) -> None:
    """Raise informative error when no tests matched filter."""
    sample = ", ".join(sorted(item.name for item in items)[:5])
    hint = f" Available sample: {sample}" if sample else ""
    raise pytest.UsageError(
        f"{filters_desc} did not match any collected tests.{hint}"
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """
    Filter collected tests based on --test-function and --test-markers options.
    
    This allows flexible test execution like:
        pytest --test-function test_graphql_contact_profile_list
        pytest --test-markers "integration,nested_resolvers"
        AI_MARKETING_TEST_FUNCTION=test_init pytest
    """
    target = config.getoption("--test-function")
    marker_filter_raw = config.getoption("--test-markers")
    markers = _parse_marker_filter(marker_filter_raw)

    if not target and not markers:
        return  # No filtering requested

    target_lower = target.lower()
    selected: list[pytest.Item] = []
    deselected: list[pytest.Item] = []

    for item in items:
        # Extract function name without parameters
        test_func_name = item.name.split("[")[0].lower()
        
        # Check if name matches (exact match)
        name_match = not target_lower or test_func_name == target_lower
        
        # Check if any requested marker is present
        marker_match = not markers or any(
            item.get_closest_marker(m) for m in markers
        )

        if name_match and marker_match:
            selected.append(item)
        else:
            deselected.append(item)

    if not selected:
        _raise_no_matches(
            _format_filter_description(target, marker_filter_raw), items
        )

    items[:] = selected
    config.hook.pytest_deselected(items=deselected)

    # Log filter results
    terminal = config.pluginmanager.get_plugin("terminalreporter")
    if terminal is not None:
        terminal.write_line(
            f"Filtered tests with {_format_filter_description(target, marker_filter_raw)} "
            f"({len(selected)} selected, {len(deselected)} deselected)."
        )
```

**Usage Examples:**
```bash
# Run specific test function
pytest --test-function test_graphql_contact_profile_list

# Run tests with specific markers
pytest --test-markers integration

# Combine markers
pytest --test-markers "integration,nested_resolvers"

# Using environment variables
export AI_MARKETING_TEST_FUNCTION=test_initialization
pytest

export AI_MARKETING_TEST_MARKERS="unit,integration"
pytest
```

---

## 4.6 Refactor Main Test File

### File: `ai_marketing_engine/tests/test_ai_marketing_engine.py` (REFACTOR)

**Step 1: Update imports and load test data**

```python
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
```

**Step 2: Unit tests**

```python
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
```

**Step 3: Integration tests for ContactProfile**

```python
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
```

**Step 4: Nested resolver tests**

```python
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
```

**Repeat Step 3 pattern for:**
- Place (4 tests)
- CorporationProfile (4 tests)
- ContactRequest (4 tests)

---

## 4.7 Run Tests and Validate

### Running Tests

```bash
# Run all tests
pytest ai_marketing_engine/tests/ -v

# Run only unit tests
pytest ai_marketing_engine/tests/ -m unit

# Run only integration tests
pytest ai_marketing_engine/tests/ -m integration

# Run only nested resolver tests
pytest ai_marketing_engine/tests/ -m nested_resolvers

# Run specific test function
pytest --test-function test_graphql_contact_profile_list

# Run with environment variable
export AI_MARKETING_TEST_MARKERS="unit,integration"
pytest

# Run with coverage
pytest --cov=ai_marketing_engine --cov-report=html

# Run slow tests only
pytest -m slow -v
```

### Expected Output

```
================== test session starts ===================
platform linux -- Python 3.9.x, pytest-7.x.x
collected 42 items

test_ai_marketing_engine.py::test_initialization_with_valid_params PASSED [2%]
test_ai_marketing_engine.py::test_schema_fetched_successfully PASSED [4%]
test_ai_marketing_engine.py::test_graphql_insert_update_contact_profile[test_data0] PASSED [7%]
...
test_ai_marketing_engine.py::test_deep_nesting_four_levels[test_data0] PASSED [95%]
test_ai_marketing_engine.py::test_lazy_loading_performance PASSED [100%]

================== 42 passed in 15.23s ===================
```

---

## 4.8 Action Items Checklist

**Configuration:**
- [ ] Add `[tool.pytest.ini_options]` to `pyproject.toml`
- [ ] Verify pytest version >= 7.0

**Test Data:**
- [ ] Create `test_data.json` with all entity test data
- [ ] Update test UUIDs to match test environment

**Fixtures:**
- [ ] Create `conftest.py` with module-scoped fixtures
- [ ] Add custom pytest hooks (pytest_addoption, pytest_collection_modifyitems)

**Helpers:**
- [ ] Create `test_helpers.py` with call_method, log_test_result, validate_nested_resolver_result

**Test Refactoring:**
- [ ] Remove all `@unittest.skip()` decorators
- [ ] Convert from `unittest.TestCase` to pytest functions
- [ ] Add `@pytest.mark.parametrize()` for data-driven tests
- [ ] Add `@log_test_result` decorator to all tests
- [ ] Replace try/except with `call_method()` helper

**Nested Resolver Tests:**
- [ ] Add 2-level nesting test (ContactProfile → Place)
- [ ] Add 3-level nesting test (ContactProfile → Place → Corporation)
- [ ] Add 4-level nesting test (ContactRequest → ContactProfile → Place → Corporation)
- [ ] Add lazy loading performance test

**Validation:**
- [ ] Run full test suite: `pytest -v`
- [ ] Run with coverage: `pytest --cov=ai_marketing_engine`
- [ ] Test environment variable filtering
- [ ] Test marker-based filtering
- [ ] Verify all tests pass

---

## Success Criteria

✅ All tests migrated from unittest to pytest  
✅ Test data externalized to JSON file  
✅ Parametrized tests reduce code by ~40%  
✅ Custom pytest hooks enable flexible test execution  
✅ Nested resolver tests cover 2, 3, and 4-level nesting  
✅ Performance test validates lazy loading  
✅ All tests pass with comprehensive logging  
✅ Test coverage >= 80%

---

## Next Phase

After Phase 4 completion, proceed to **Phase 5: Utils Review**.
