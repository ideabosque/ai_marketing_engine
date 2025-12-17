#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Pytest configuration and fixtures for AI Marketing Engine tests."""
from __future__ import annotations

__author__ = "bibow"

import json
import logging
import os
import re
import sys
from typing import Any, Dict, Sequence

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
# Use absolute path relative to this conftest file to ensure imports work
# regardless of where pytest is run from
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../silvaengine_dynamodb_base")
    ),
)
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../silvaengine_utility")
    ),
)

from silvaengine_utility.graphql import Graphql

from ai_marketing_engine import AIMarketingEngine

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
    "part_id": os.getenv("part_id"),
    "execute_mode": os.getenv("execute_mode", "local"),
    "initialize_tables": int(os.getenv("initialize_tables", "0")),
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

    try:
        context = {
            "endpoint_id": endpoint_id,
            "setting": SETTING,
            "logger": logger,
        }

        schema = Graphql.fetch_graphql_schema(
            context,
            "ai_marketing_graphql",
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


# ============================================================================
# CUSTOM PYTEST HOOKS
# ============================================================================

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
    raise pytest.UsageError(f"{filters_desc} did not match any collected tests.{hint}")


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
        marker_match = not markers or any(item.get_closest_marker(m) for m in markers)

        if name_match and marker_match:
            selected.append(item)
        else:
            deselected.append(item)

    if not selected:
        _raise_no_matches(_format_filter_description(target, marker_filter_raw), items)

    items[:] = selected
    config.hook.pytest_deselected(items=deselected)

    # Log filter results
    terminal = config.pluginmanager.get_plugin("terminalreporter")
    if terminal is not None:
        terminal.write_line(
            f"Filtered tests with {_format_filter_description(target, marker_filter_raw)} "
            f"({len(selected)} selected, {len(deselected)} deselected)."
        )
