#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Unit tests for batch loaders (DataLoader implementations)."""
from __future__ import annotations

__author__ = "bibow"

import sys
import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from promise import Promise

# Add parent directory to path to allow imports when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from silvaengine_utility import Utility

from ai_marketing_engine.models.batch_loaders import (
    RequestLoaders,
    clear_loaders,
    get_loaders,
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _mock_model(endpoint_id: str, range_attr: str, range_value: str, **extra: Any) -> Any:
    """Build a lightweight mock Pynamo model with attribute_values."""

    # Use a simple class instead of MagicMock to avoid __dict__ issues
    class MockModel:
        pass

    model = MockModel()
    model.endpoint_id = endpoint_id
    setattr(model, range_attr, range_value)
    model.__dict__["attribute_values"] = {
        "endpoint_id": endpoint_id,
        range_attr: range_value,
        **extra,
    }
    return model


# ============================================================================
# BATCH LOADER UNIT TESTS
# ============================================================================


@pytest.mark.unit
def test_batch_loaders_cached_per_context() -> None:
    """Test that loaders are cached per context and can be cleared."""
    context = {}
    first = get_loaders(context)
    second = get_loaders(context)
    assert first is second
    clear_loaders(context)
    third = get_loaders(context)
    assert third is not first


@pytest.mark.unit
def test_place_loader_batches_requests() -> None:
    """Test that PlaceLoader successfully loads multiple places and deduplicates requests."""
    from ai_marketing_engine.models.batch_loaders import PlaceLoader

    context = {"logger": MagicMock()}
    loader = PlaceLoader(logger=context["logger"])

    p1 = _mock_model("endpoint-1", "place_uuid", "place-1", business_name="Place 1")
    p2 = _mock_model("endpoint-1", "place_uuid", "place-2", business_name="Place 2")

    # Verify mock models are correct
    assert p1.endpoint_id == "endpoint-1", "Mock p1 endpoint_id not set"
    assert p1.place_uuid == "place-1", "Mock p1 place_uuid not set"
    normalized_p1 = Utility.json_normalize(p1.__dict__["attribute_values"])
    assert (
        normalized_p1["place_uuid"] == "place-1"
    ), f"Normalized p1 incorrect: {normalized_p1}"

    with patch("ai_marketing_engine.models.place.PlaceModel.batch_get") as mock_batch:
        # Mock should return an iterable of models
        mock_batch.return_value = [p1, p2]

        # Test the batch_load_fn directly
        keys = [("endpoint-1", "place-1"), ("endpoint-1", "place-2")]
        result_promise = loader.batch_load_fn(keys)
        results = result_promise.get()

    # Verify batch_get was called once
    assert mock_batch.call_count == 1, f"Expected 1 call, got {mock_batch.call_count}"

    # Debug output
    if results[0] is None:
        print(f"Results: {results}")
        print(f"Mock was called with: {mock_batch.call_args_list}")

    # Verify results match keys
    assert (
        results[0] is not None
    ), f"First result should not be None. Results: {results}"
    assert (
        results[0]["place_uuid"] == "place-1"
    ), f"Expected place-1, got {results[0].get('place_uuid')}"
    assert (
        results[1]["place_uuid"] == "place-2"
    ), f"Expected place-2, got {results[1].get('place_uuid')}"


@pytest.mark.unit
def test_corporation_loader_batches_requests() -> None:
    """Test that CorporationProfileLoader successfully loads multiple corporations."""
    from ai_marketing_engine.models.batch_loaders import CorporationProfileLoader

    context = {"logger": MagicMock()}
    loader = CorporationProfileLoader(logger=context["logger"])

    c1 = _mock_model("endpoint-1", "corporation_uuid", "corp-1", business_name="One")
    c2 = _mock_model("endpoint-1", "corporation_uuid", "corp-2", business_name="Two")

    with patch(
        "ai_marketing_engine.models.corporation_profile.CorporationProfileModel.batch_get"
    ) as mock_batch:
        mock_batch.return_value = [c1, c2]

        # Test the batch_load_fn directly
        keys = [("endpoint-1", "corp-1"), ("endpoint-1", "corp-2")]
        result_promise = loader.batch_load_fn(keys)
        results = result_promise.get()

    # Verify batch_get was called once
    assert mock_batch.call_count == 1, f"Expected 1 call, got {mock_batch.call_count}"

    # Verify results match keys
    assert results[0] is not None, "First result should not be None"
    assert results[0]["corporation_uuid"] == "corp-1"
    assert results[1]["business_name"] == "Two"


@pytest.mark.unit
def test_attribute_loader_deduplicates_keys() -> None:
    """Test that attribute loaders deduplicate identical keys."""
    context = {"logger": MagicMock()}
    loaders = RequestLoaders(context)

    with patch("ai_marketing_engine.models.utils._get_data") as mock_get_data:
        mock_get_data.return_value = {"foo": "bar"}

        results = Promise.all(
            [
                loaders.contact_data_loader.load(("endpoint-1", "contact-1")),
                loaders.contact_data_loader.load(("endpoint-1", "contact-1")),
            ]
        ).get()

    assert mock_get_data.call_count == 1
    assert results[0] == {"foo": "bar"}
    assert results[1] == {"foo": "bar"}


# ============================================================================
# MAIN ENTRY POINT FOR DIRECT EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Run batch loader tests directly with Python for debugging and development.

    Usage:
        python test_batch_loaders.py              # Run all batch loader tests
        python test_batch_loaders.py -v           # Verbose output
        python test_batch_loaders.py -k test_place # Run specific test
        python test_batch_loaders.py -s           # Show print statements

    Examples:
        python test_batch_loaders.py -v
        python test_batch_loaders.py -k "test_place_loader" -s
    """
    import sys

    # Run pytest with this file
    sys.exit(pytest.main([__file__, "-v"] + sys.argv[1:]))
