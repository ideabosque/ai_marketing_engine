#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for cache management system."""
from __future__ import annotations

__author__ = "bibow"

import json
import logging
import os
import sys
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add parent directory to path to allow imports when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ai_marketing_engine.handlers.config import Config
from ai_marketing_engine.models.cache import (
    _get_cascading_cache_purger,
    purge_entity_cascading_cache,
)



class TestCacheManagement:
    """Test suite for cache management functionality."""

    @pytest.fixture
    def mock_logger(self):
        """Mock logger for testing."""
        return Mock(spec=logging.Logger)

    @pytest.fixture
    def sample_context_keys(self):
        """Sample context keys for testing."""
        return {"endpoint_id": "test-endpoint"}

    @pytest.fixture
    def sample_entity_keys(self):
        """Sample entity keys for testing."""
        return {"corporation_uuid": "test-corp-123"}

    def test_get_cascading_cache_purger_singleton(self):
        """Test that _get_cascading_cache_purger returns singleton instance."""
        purger1 = _get_cascading_cache_purger()
        purger2 = _get_cascading_cache_purger()
        assert purger1 is purger2

    @patch("ai_marketing_engine.models.cache.CascadingCachePurger")
    @patch("ai_marketing_engine.models.cache.CacheConfigResolvers")
    def test_get_cascading_cache_purger_initialization(
        self, mock_resolvers, mock_purger
    ):
        """Test proper initialization of CascadingCachePurger."""
        # Clear LRU cache to force re-initialization
        _get_cascading_cache_purger.cache_clear()

        mock_purger_instance = Mock()
        mock_purger.return_value = mock_purger_instance
        mock_resolvers_instance = Mock()
        mock_resolvers.return_value = mock_resolvers_instance

        result = _get_cascading_cache_purger()

        mock_resolvers.assert_called_once_with(
            get_cache_entity_config=Config.get_cache_entity_config,
            get_cache_relationships=Config.get_cache_relationships,
            queries_module_base="ai_marketing_engine.queries",
        )
        mock_purger.assert_called_once_with(mock_resolvers_instance)
        assert result is mock_purger_instance

    @patch("ai_marketing_engine.models.cache._get_cascading_cache_purger")
    def test_purge_entity_cascading_cache_basic(
        self, mock_get_purger, mock_logger, sample_context_keys, sample_entity_keys
    ):
        """Test basic purge_entity_cascading_cache functionality."""
        mock_purger = Mock()
        mock_get_purger.return_value = mock_purger
        expected_result = {"purged_keys": ["key1", "key2"]}
        mock_purger.purge_entity_cascading_cache.return_value = expected_result

        result = purge_entity_cascading_cache(
            mock_logger,
            "corporation_profile",
            context_keys=sample_context_keys,
            entity_keys=sample_entity_keys,
        )

        mock_purger.purge_entity_cascading_cache.assert_called_once_with(
            mock_logger,
            "corporation_profile",
            context_keys=sample_context_keys,
            entity_keys=sample_entity_keys,
            cascade_depth=3,
        )
        assert result == expected_result

    @patch("ai_marketing_engine.models.cache._get_cascading_cache_purger")
    def test_purge_entity_cascading_cache_custom_depth(
        self, mock_get_purger, mock_logger
    ):
        """Test purge with custom cascade depth."""
        mock_purger = Mock()
        mock_get_purger.return_value = mock_purger
        mock_purger.purge_entity_cascading_cache.return_value = {}

        purge_entity_cascading_cache(
            mock_logger,
            "place",
            cascade_depth=5,
        )

        mock_purger.purge_entity_cascading_cache.assert_called_once_with(
            mock_logger,
            "place",
            context_keys=None,
            entity_keys=None,
            cascade_depth=5,
        )

    def test_config_cache_methods(self):
        """Test Config class cache-related methods."""
        # Test cache entity config
        entity_config = Config.get_cache_entity_config()
        assert isinstance(entity_config, dict)
        assert "corporation_profile" in entity_config
        assert "place" in entity_config
        assert "contact_profile" in entity_config

        # Test cache relationships
        relationships = Config.get_cache_relationships()
        assert isinstance(relationships, dict)
        assert "corporation_profile" in relationships
        assert "place" in relationships

        # Test cache name generation
        cache_name = Config.get_cache_name("models", "corporation_profile")
        assert cache_name == "ai_marketing_engine.models.corporation_profile"

        # Test cache TTL
        ttl = Config.get_cache_ttl()
        assert isinstance(ttl, int)
        assert ttl > 0

        # Test cache enabled
        enabled = Config.is_cache_enabled()
        assert isinstance(enabled, bool)

        # Test entity children
        children = Config.get_entity_children("corporation_profile")
        assert isinstance(children, list)


class TestBatchLoaderCache:
    """Test suite for batch loader cache functionality."""

    @pytest.fixture
    def mock_cache_engine(self):
        """Mock HybridCacheEngine for testing."""
        return Mock()

    @pytest.fixture
    def mock_request_loaders(self, mock_cache_engine):
        """Mock RequestLoaders instance."""
        with patch(
            "ai_marketing_engine.models.batch_loaders.HybridCacheEngine"
        ) as mock_engine_class:
            mock_engine_class.return_value = mock_cache_engine
            from ai_marketing_engine.models.batch_loaders import RequestLoaders

            return RequestLoaders({"logger": Mock(), "endpoint_id": "test-endpoint"})

    def test_request_loaders_initialization(self, mock_request_loaders):
        """Test RequestLoaders initialization with cache engine."""

    @patch(
        "ai_marketing_engine.models.batch_loaders.Config.is_cache_enabled",
        return_value=True,
    )
    @patch("ai_marketing_engine.models.place.PlaceModel")
    def test_dataloader_cache_interaction(
        self, mock_place_model, mock_is_cache_enabled, mock_request_loaders
    ):
        """Test that data loaders correctly interact with the HybridCacheEngine."""
        mock_cache_instance = Mock()
        mock_request_loaders.place_loader.cache = mock_cache_instance

        # Simulate cache hit
        mock_cache_instance.get.return_value = {"cached": "data"}
        keys = [("test-endpoint", "place-1")]
        result = mock_request_loaders.place_loader.batch_load_fn(keys).value
        assert result == [{"cached": "data"}]
        mock_cache_instance.get.assert_called_with("test-endpoint:place-1")
        mock_place_model.batch_get.assert_not_called()

        # Simulate cache miss and then set
        mock_cache_instance.get.return_value = None
        mock_place_model.batch_get.return_value = [
            Mock(
                endpoint_id="test-endpoint",
                place_uuid="place-2",
                attribute_values={"new": "data"},
            )
        ]
        keys = [("test-endpoint", "place-2")]
        result = mock_request_loaders.place_loader.batch_load_fn(keys).value
        assert result == [{"new": "data"}]
        mock_cache_instance.get.assert_called_with("test-endpoint:place-2")
        mock_place_model.batch_get.assert_called_once_with(
            [("test-endpoint", "place-2")]
        )
        mock_cache_instance.set.assert_called_once()


class TestCacheDecorators:
    """Test suite for cache decorators (@method_cache, @purge_cache)."""

    @pytest.fixture
    def mock_model_instance(self):
        """Mock model instance for testing decorators."""
        return Mock()

    def test_cache_integration_in_models(self):
        """Test that cache decorators are integrated in model methods."""
        from ai_marketing_engine.models.corporation_profile import (
            CorporationProfileModel,
        )

        # Check that the model class exists and has expected methods


class TestCacheConfiguration:
    """Test suite for cache configuration validation."""

    def test_cache_entity_config_structure(self):
        """Test that CACHE_ENTITY_CONFIG has proper structure."""
        config = Config.get_cache_entity_config()

        for entity_type, entity_config in config.items():
            # Verify required keys exist
            required_keys = [
                "module",
                "model_class",
                "getter",
                "list_resolver",
                "cache_keys",
            ]
            for key in required_keys:
                assert key in entity_config, f"Missing {key} in {entity_type} config"

            # Verify cache_keys is a list
            assert isinstance(entity_config["cache_keys"], list)
            assert len(entity_config["cache_keys"]) > 0

    def test_cache_relationships_structure(self):
        """Test that CACHE_RELATIONSHIPS has proper structure."""
        relationships = Config.get_cache_relationships()

        for parent_entity, children in relationships.items():
            assert isinstance(children, list)
            for child in children:
                required_keys = [
                    "entity_type",
                    "list_resolver",
                    "module",
                    "dependency_key",
                ]
                for key in required_keys:
                    assert (
                        key in child
                    ), f"Missing {key} in {parent_entity} relationship"

    def test_cache_names_generation(self):
        """Test cache name generation for different modules."""
        # Test models cache name
        models_name = Config.get_cache_name("models", "corporation_profile")
        assert models_name == "ai_marketing_engine.models.corporation_profile"

        # Test queries cache name
        queries_name = Config.get_cache_name("queries", "place")
        assert queries_name == "ai_marketing_engine.queries.place"

        # Test unknown module type
        unknown_name = Config.get_cache_name("unknown", "test")
        assert unknown_name == "ai_marketing_engine.unknown.test"

    def test_entity_children_retrieval(self):
        """Test retrieval of entity children."""
        # Test existing entity
        corp_children = Config.get_entity_children("corporation_profile")
        assert isinstance(corp_children, list)
        assert len(corp_children) > 0

        # Test non-existing entity
        empty_children = Config.get_entity_children("non_existing_entity")
        assert empty_children == []


@pytest.mark.integration
class TestCacheIntegration:
    """Integration tests for cache system."""

    def test_cache_system_integration(self, ai_marketing_engine):
        """Test cache system integration demonstrating cache behavior."""
        if not hasattr(ai_marketing_engine, "__is_real__"):
            pytest.skip("Real AI Marketing Engine instance not available")

        import uuid
        from unittest.mock import patch

        # Test cache configuration is accessible
        with open("debug_output.txt", "w") as f:
            f.write(f"Config.is_cache_enabled() = {Config.is_cache_enabled()}\n")
            f.write(f"Config.get_cache_ttl() = {Config.get_cache_ttl()}\n")
            from ai_marketing_engine.models.corporation_profile import get_corporation_profile
            f.write(f"get_corporation_profile = {get_corporation_profile}\n")
            f.write(f"get_corporation_profile type = {type(get_corporation_profile)}\n")
            f.write(f"Has cache_clear: {hasattr(get_corporation_profile, 'cache_clear')}\n")
            f.write(f"Has cache_info: {hasattr(get_corporation_profile, 'cache_info')}\n")

        assert Config.is_cache_enabled() is not None
        assert Config.get_cache_ttl() > 0
        assert isinstance(Config.get_cache_entity_config(), dict)
        assert isinstance(Config.get_cache_relationships(), dict)

        # Test cache purger can be initialized
        purger = _get_cascading_cache_purger()
        assert purger is not None

        # Test cache purge function works
        corp_uuid = str(uuid.uuid4())
        purge_result = purge_entity_cascading_cache(
            ai_marketing_engine.logger,
            "corporation_profile",
            context_keys={"endpoint_id": ai_marketing_engine.setting.get("endpoint_id")},
            entity_keys={"corporation_uuid": corp_uuid}
        )
        assert purge_result is not None

        # Test that cache decorators are working by checking function calls
        # We patch the underlying model method, NOT the decorated function
        with patch("ai_marketing_engine.models.corporation_profile.CorporationProfileModel.get") as mock_get:
            # Mock return value - use a simple class that is picklable/cacheable
            class MockModel:
                def __init__(self, uuid):
                    self.attribute_values = {
                        "corporation_uuid": uuid,
                        "business_name": "Test Corp",
                        "corporation_type": "TEST"
                    }
            
            mock_instance = MockModel(corp_uuid)
            mock_get.return_value = mock_instance

            # Call the function twice - first should call mock, second should use cache
            from ai_marketing_engine.models.corporation_profile import get_corporation_profile
            
            # First call - should hit the "database" (mock)
            result1 = get_corporation_profile(
                endpoint_id=ai_marketing_engine.setting.get("endpoint_id"),
                corporation_uuid=corp_uuid
            )
            assert result1 is not None
            assert mock_get.call_count == 1

            # Second call - should use cache and NOT hit the "database" (mock)
            result2 = get_corporation_profile(
                endpoint_id=ai_marketing_engine.setting.get("endpoint_id"),
                corporation_uuid=corp_uuid
            )
            assert result2 is not None
            # Call count should STILL be 1 if cache is working
            assert mock_get.call_count == 1


# ============================================================================
# MAIN ENTRY POINT FOR DIRECT EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Run cache management tests directly with Python for debugging and development.

    Usage:
        python test_cache_management.py              # Run all cache tests
        python test_cache_management.py -v           # Verbose output
        python test_cache_management.py -k test_cache # Run specific test
        python test_cache_management.py -s           # Show print statements

    Examples:
        python test_cache_management.py -v
        python test_cache_management.py -k "test_purge" -s
    """
    import sys

    # Run pytest with this file
    sys.exit(pytest.main([__file__, "-v"] + sys.argv[1:]))