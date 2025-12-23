# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
import os
from typing import Any, Dict, List

import boto3

from ..models import utils


class Config:
    """
    Centralized Configuration Class
    Manages shared configuration variables across the application.
    """

    aws_lambda = None
    aws_s3 = None
    # schemas = {}
    module_bucket_name = None
    module_zip_path = None
    module_extract_path = None

    # Cache Configuration
    CACHE_TTL = 1800  # 30 minutes default TTL
    CACHE_ENABLED = True

    # Cache name patterns for different modules
    CACHE_NAMES = {
        "models": "ai_marketing_engine.models",
        "queries": "ai_marketing_engine.queries",
    }

    # Cache entity metadata (module paths, getters, cache key templates)
    CACHE_ENTITY_CONFIG = {
        "corporation_profile": {
            "module": "ai_marketing_engine.models.corporation_profile",
            "model_class": "CorporationProfileModel",
            "getter": "get_corporation_profile",
            "list_resolver": "ai_marketing_engine.queries.corporation_profile.resolve_corporation_profile_list",
            "cache_keys": ["context:endpoint_id", "key:corporation_uuid"],
        },
        "place": {
            "module": "ai_marketing_engine.models.place",
            "model_class": "PlaceModel",
            "getter": "get_place",
            "list_resolver": "ai_marketing_engine.queries.place.resolve_place_list",
            "cache_keys": ["context:endpoint_id", "key:place_uuid"],
        },
        "contact_profile": {
            "module": "ai_marketing_engine.models.contact_profile",
            "model_class": "ContactProfileModel",
            "getter": "get_contact_profile",
            "list_resolver": "ai_marketing_engine.queries.contact_profile.resolve_contact_profile_list",
            "cache_keys": ["context:endpoint_id", "key:contact_uuid"],
        },
        "contact_request": {
            "module": "ai_marketing_engine.models.contact_request",
            "model_class": "ContactRequestModel",
            "getter": "get_contact_request",
            "list_resolver": "ai_marketing_engine.queries.contact_request.resolve_contact_request_list",
            "cache_keys": ["context:endpoint_id", "key:request_uuid"],
        },
        "attribute_value": {
            "module": "ai_marketing_engine.models.attribute_value",
            "model_class": "AttributeValueModel",
            "getter": "get_attribute_value",
            "list_resolver": "ai_marketing_engine.queries.attribute_value.resolve_attribute_value_list",
            "cache_keys": ["key:data_type_attribute_name", "key:value_version_uuid"],
        },
        "activity_history": {
            "module": "ai_marketing_engine.models.activity_history",
            "model_class": "ActivityHistoryModel",
            "getter": "get_activity_history",
            "list_resolver": "ai_marketing_engine.queries.activity_history.resolve_activity_history_list",
            "cache_keys": ["key:id", "key:timestamp"],
        },
        "attributes_data": {
            "module": "ai_marketing_engine.models.attribute_value",
            "model_class": "AttributeValueModel",
            "getter": "get_attributes_data",
            # "list_resolver": "ai_marketing_engine.queries.attribute_value.resolve_attribute_value_list",
            "cache_keys": ["context:endpoint_id", "key:data_identity", "key:data_type"],
        },
    }

    # Entity cache dependency relationships
    CACHE_RELATIONSHIPS = {
        "corporation_profile": [
            {
                "entity_type": "place",
                "list_resolver": "resolve_place_list",
                "module": "place",
                "dependency_key": "corporation_uuid",
            },
            {
                "entity_type": "attribute_value",
                "list_resolver": "resolve_attribute_value_list",
                "module": "attribute_value",
                "dependency_key": "data_identity",
                "parent_key": "corporation_uuid",
            },
        ],
        "place": [
            {
                "entity_type": "contact_profile",
                "list_resolver": "resolve_contact_profile_list",
                "module": "contact_profile",
                "dependency_key": "place_uuid",
            },
            {
                "entity_type": "contact_request",
                "list_resolver": "resolve_contact_request_list",
                "module": "contact_request",
                "dependency_key": "place_uuid",
            },
        ],
        "contact_profile": [
            {
                "entity_type": "contact_request",
                "list_resolver": "resolve_contact_request_list",
                "module": "contact_request",
                "dependency_key": "contact_uuid",
            },
            {
                "entity_type": "attribute_value",
                "list_resolver": "resolve_attribute_value_list",
                "module": "attribute_value",
                "dependency_key": "data_identity",
                "parent_key": "contact_uuid",
            },
        ],
    }

    @classmethod
    def initialize(cls, logger: logging.Logger, **setting: Dict[str, Any]) -> None:
        """
        Initialize configuration setting.
        Args:
            logger (logging.Logger): Logger instance for logging.
            **setting (Dict[str, Any]): Configuration dictionary.
        """
        try:
            cls._set_parameters(setting)
            cls._setup_function_paths(setting)
            cls._initialize_aws_services(setting)
            if setting.get("initialize_tables"):
                cls._initialize_tables(logger)
            logger.info("Configuration initialized successfully.")
        except Exception as e:
            logger.exception("Failed to initialize configuration.")
            raise e

    @classmethod
    def _set_parameters(cls, setting: Dict[str, Any]) -> None:
        """
        Set application-level parameters.
        Args:
            setting (Dict[str, Any]): Configuration dictionary.
        """
        pass

    @classmethod
    def _setup_function_paths(cls, setting: Dict[str, Any]) -> None:
        cls.module_bucket_name = setting.get("module_bucket_name")
        cls.module_zip_path = setting.get("module_zip_path", "/tmp/adaptor_zips")
        cls.module_extract_path = setting.get("module_extract_path", "/tmp/adaptors")
        os.makedirs(cls.module_zip_path, exist_ok=True)
        os.makedirs(cls.module_extract_path, exist_ok=True)

    @classmethod
    def _initialize_tables(cls, logger: logging.Logger) -> None:
        """
        Initialize database tables by calling the utils._initialize_tables() method.
        This is an internal method used during configuration setup.
        """
        utils._initialize_tables(logger)

    @classmethod
    def _initialize_aws_services(cls, setting: Dict[str, Any]) -> None:
        """
        Initialize AWS services, such as the S3 client.
        Args:
            setting (Dict[str, Any]): Configuration dictionary.
        """
        if all(
            setting.get(k)
            for k in ["region_name", "aws_access_key_id", "aws_secret_access_key"]
        ):
            aws_credentials = {
                "region_name": setting["region_name"],
                "aws_access_key_id": setting["aws_access_key_id"],
                "aws_secret_access_key": setting["aws_secret_access_key"],
            }
        else:
            aws_credentials = {}

        cls.aws_lambda = boto3.client("lambda", **aws_credentials)
        cls.aws_s3 = boto3.client(
            "s3",
            **aws_credentials,
            config=boto3.session.Config(signature_version="s3v4"),
        )

    @classmethod
    def get_cache_entity_config(cls) -> Dict[str, Dict[str, Any]]:
        """Get cache configuration metadata for each entity type."""
        return cls.CACHE_ENTITY_CONFIG

    @classmethod
    def get_cache_name(cls, module_type: str, model_name: str) -> str:
        """
        Generate standardized cache names.

        Args:
            module_type: 'models' or 'queries'
            model_name: Name of the model (e.g., 'corporation_profile', 'place')

        Returns:
            Standardized cache name string
        """
        base_name = cls.CACHE_NAMES.get(
            module_type, f"ai_marketing_engine.{module_type}"
        )
        return f"{base_name}.{model_name}"

    @classmethod
    def get_cache_ttl(cls) -> int:
        """Get the configured cache TTL."""
        return cls.CACHE_TTL

    @classmethod
    def is_cache_enabled(cls) -> bool:
        """Check if caching is enabled."""
        return cls.CACHE_ENABLED

    @classmethod
    def get_cache_relationships(cls) -> Dict[str, List[Dict[str, str]]]:
        """Get entity cache dependency relationships."""
        return cls.CACHE_RELATIONSHIPS

    @classmethod
    def get_entity_children(cls, entity_type: str) -> List[Dict[str, str]]:
        """Get child entities for a specific entity type."""
        return cls.CACHE_RELATIONSHIPS.get(entity_type, [])
