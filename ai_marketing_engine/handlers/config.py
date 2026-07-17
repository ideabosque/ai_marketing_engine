# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
import os
from typing import Any, Dict, List

import boto3


class Config:
    """
    Centralized Configuration Class
    Manages shared configuration variables across the application.
    """

    aws_lambda = None
    aws_s3 = None
    aws_ses = None
    # schemas = {}
    module_bucket_name = None
    module_zip_path = None
    module_extract_path = None

    # Dual-backend selection: "dynamodb" (default) or "postgresql"
    DB_BACKEND: str = "dynamodb"
    db_session = None  # PostgreSQL scoped_session (only set in PG mode)
    _db_engine = None
    PG_TABLE_PREFIX: str = "ame_"

    # Initialization state (for gateway dispatch_graphql)
    _initialized: bool = False
    _setting: Dict[str, Any] = {}
    _logger = None

    # Cache Configuration
    CACHE_TTL = 1800  # 30 minutes default TTL
    CACHE_ENABLED = True

    # Cache name patterns for different modules
    CACHE_NAMES = {
        "models": "ai_marketing_engine.models.dynamodb",
        "queries": "ai_marketing_engine.queries",
    }

    # Cache entity metadata (module paths, getters, cache key templates)
    CACHE_ENTITY_CONFIG = {
        "corporation_profile": {
            "module": "ai_marketing_engine.models.dynamodb.corporation_profile",
            "model_class": "CorporationProfileModel",
            "getter": "get_corporation_profile",
            "list_resolver": "ai_marketing_engine.queries.corporation_profile.resolve_corporation_profile_list",
            "cache_keys": ["context:endpoint_id", "key:corporation_uuid"],
        },
        "place": {
            "module": "ai_marketing_engine.models.dynamodb.place",
            "model_class": "PlaceModel",
            "getter": "get_place",
            "list_resolver": "ai_marketing_engine.queries.place.resolve_place_list",
            "cache_keys": ["context:endpoint_id", "key:place_uuid"],
        },
        "contact_profile": {
            "module": "ai_marketing_engine.models.dynamodb.contact_profile",
            "model_class": "ContactProfileModel",
            "getter": "get_contact_profile",
            "list_resolver": "ai_marketing_engine.queries.contact_profile.resolve_contact_profile_list",
            "cache_keys": ["context:endpoint_id", "key:contact_uuid"],
        },
        "contact_request": {
            "module": "ai_marketing_engine.models.dynamodb.contact_request",
            "model_class": "ContactRequestModel",
            "getter": "get_contact_request",
            "list_resolver": "ai_marketing_engine.queries.contact_request.resolve_contact_request_list",
            "cache_keys": ["context:endpoint_id", "key:request_uuid"],
        },
        "attribute_value": {
            "module": "ai_marketing_engine.models.dynamodb.attribute_value",
            "model_class": "AttributeValueModel",
            "getter": "get_attribute_value",
            "list_resolver": "ai_marketing_engine.queries.attribute_value.resolve_attribute_value_list",
            "cache_keys": ["key:data_type_attribute_name", "key:value_version_uuid"],
        },
        "activity_history": {
            "module": "ai_marketing_engine.models.dynamodb.activity_history",
            "model_class": "ActivityHistoryModel",
            "getter": "get_activity_history",
            "list_resolver": "ai_marketing_engine.queries.activity_history.resolve_activity_history_list",
            "cache_keys": ["key:id", "key:timestamp"],
        },
        "attributes_data": {
            "module": "ai_marketing_engine.models.dynamodb.attribute_value",
            "model_class": "AttributeValueModel",
            "getter": "get_attributes_data",
            # "list_resolver": "ai_marketing_engine.queries.attribute_value.resolve_attribute_value_list",
            "cache_keys": ["context:endpoint_id", "key:data_identity", "key:data_type"],
        },
    }

    # PostgreSQL cache config — empty because PG repos don't use @method_cache.
    CACHE_ENTITY_CONFIG_POSTGRESQL: Dict[str, Dict[str, Any]] = {}

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

    # PostgreSQL cascade relationships — empty until PG repos cache resolvers.
    CACHE_RELATIONSHIPS_POSTGRESQL: Dict[str, List[Dict[str, Any]]] = {}

    @classmethod
    def initialize(cls, logger: logging.Logger, **setting: Dict[str, Any]) -> None:
        """
        Initialize configuration setting.

        Backend selection is driven by ``setting["db_backend"]``:
        - ``dynamodb`` (default): preserves current PynamoDB behavior.
        - ``postgresql``: uses a SQLAlchemy scoped session for persistence.

        Args:
            logger (logging.Logger): Logger instance for logging.
            **setting (Dict[str, Any]): Configuration dictionary.
        """
        # Idempotent: the gateway constructs a fresh engine per request, so
        # without this guard the AWS clients and SQLAlchemy engine would be
        # rebuilt on every call.
        if cls._initialized:
            return
        try:
            cls._logger = logger
            cls._setting = dict(setting)
            cls._set_parameters(setting)
            cls._setup_function_paths(setting)

            # Backend selection (deployment-time, not per request)
            cls.DB_BACKEND = str(setting.get("db_backend", "dynamodb")).lower()
            if cls.DB_BACKEND not in ("dynamodb", "postgresql"):
                raise ValueError(f"Unknown db_backend: {cls.DB_BACKEND}")
            cls.PG_TABLE_PREFIX = str(setting.get("pg_table_prefix", "ame_")).strip()

            if cls.DB_BACKEND == "postgresql":
                cls._initialize_db_session(setting)

            # AWS service clients (SES/S3/Lambda) are backend-independent.
            cls._initialize_aws_services(setting)

            if setting.get("initialize_tables"):
                cls._initialize_tables(logger)

            cls._initialized = True
            logger.info(
                f"Configuration initialized successfully (db_backend={cls.DB_BACKEND})."
            )
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
        # Set cache enabled flag (defaults to True if not specified)
        if "cache_enabled" in setting:
            cls.CACHE_ENABLED = setting.get("cache_enabled", True)

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
        Initialize database tables — dispatched by backend.
        This is an internal method used during configuration setup.
        """
        if cls.DB_BACKEND == "dynamodb":
            from ..models.dynamodb import utils

            utils.initialize_tables(logger)
        elif cls.DB_BACKEND == "postgresql":
            from ..models.postgresql.utils import initialize_tables as pg_init

            pg_init(logger, cls.db_session, cls._db_engine)

    @classmethod
    def _initialize_db_session(cls, setting: Dict[str, Any]) -> None:
        """Initialize the PostgreSQL SQLAlchemy scoped_session.

        Expected setting keys: db_host, db_port, db_user, db_password, db_schema,
        and optionally pg_table_prefix / database_url.
        """
        from urllib.parse import quote_plus

        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker

        from ..models.postgresql.base import Base

        # Set the table prefix before any PG models are imported.
        Base.table_prefix = cls.PG_TABLE_PREFIX

        database_url = setting.get("database_url")
        if database_url:
            connection_string = database_url
        else:
            password = quote_plus(str(setting.get("db_password", "")))
            connection_string = (
                f"postgresql+psycopg2://{setting.get('db_user', 'silvaengine')}:{password}"
                f"@{setting.get('db_host', 'localhost')}:{setting.get('db_port', '5432')}"
                f"/{setting.get('db_schema', 'silvaengine')}"
            )

        engine = create_engine(
            connection_string,
            pool_recycle=7200,
            pool_size=30,
            max_overflow=20,
            pool_timeout=60,
            pool_pre_ping=True,
            echo=False,
        )
        cls.db_session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=engine)
        )
        cls._db_engine = engine

    @classmethod
    def _set_rls_context(cls, partition_key: str) -> None:
        """Set the RLS tenant context for the current PostgreSQL session."""
        if cls.DB_BACKEND == "postgresql" and cls.db_session and partition_key:
            from ..utils.rls import set_rls_context

            set_rls_context(cls.db_session, partition_key)

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
        cls.aws_ses = boto3.client("ses", **aws_credentials)

    @classmethod
    def get_cache_entity_config(cls) -> Dict[str, Dict[str, Any]]:
        """Get cache configuration metadata for each entity type (active backend)."""
        if cls.DB_BACKEND == "postgresql":
            return cls.CACHE_ENTITY_CONFIG_POSTGRESQL
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
        """Get entity cache dependency relationships (active backend)."""
        if cls.DB_BACKEND == "postgresql":
            return cls.CACHE_RELATIONSHIPS_POSTGRESQL
        return cls.CACHE_RELATIONSHIPS

    @classmethod
    def get_entity_children(cls, entity_type: str) -> List[Dict[str, str]]:
        """Get child entities for a specific entity type (active backend)."""
        return cls.get_cache_relationships().get(entity_type, [])

    @classmethod
    def get_setting(cls) -> Dict[str, Any]:
        """Return the setting dict stored at initialization time."""
        return cls._setting or {}

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Return the logger stored at initialization time."""
        return cls._logger or logging.getLogger("ai_marketing_engine")
