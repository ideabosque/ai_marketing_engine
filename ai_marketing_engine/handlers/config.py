# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
import os
from typing import Any, Dict

import boto3

from silvaengine_utility import Utility

from ..models import utils
from .ai_coordination_utility import _get_class_object


class Config:
    """
    Centralized Configuration Class
    Manages shared configuration variables across the application.
    """

    aws_lambda = None
    aws_s3 = None
    crm_connector = None
    schemas = {}
    module_bucket_name = None
    module_zip_path = None
    module_extract_path = None

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
            cls._initialize_crm_connector(logger, setting)
            if setting.get("test_mode") == "local_for_all":
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
        cls.aws_s3 = boto3.client("s3", **aws_credentials)

    @classmethod
    def _initialize_crm_connector(
        cls, logger: logging.Logger, setting: Dict[str, Any]
    ) -> None:
        if "crm_connector_config" in setting:
            cls.crm_connector = _get_class_object(
                logger,
                setting["crm_connector_config"]["module_name"],
                setting["crm_connector_config"]["class_name"],
                **setting["crm_connector_config"]["setting"],
            )

    # Fetches and caches GraphQL schema for a given function
    @classmethod
    def fetch_graphql_schema(
        cls,
        logger: logging.Logger,
        endpoint_id: str,
        function_name: str,
        setting: Dict[str, Any] = {},
    ) -> Dict[str, Any]:
        """
        Fetches and caches a GraphQL schema for a given function.

        Args:
            logger: Logger instance for error reporting
            endpoint_id: ID of the endpoint to fetch schema from
            function_name: Name of function to get schema for
            setting: Optional settings dictionary

        Returns:
            Dict containing the GraphQL schema
        """
        # Check if schema exists in cache, if not fetch and store it
        if Config.schemas.get(function_name) is None:
            Config.schemas[function_name] = Utility.fetch_graphql_schema(
                logger,
                endpoint_id,
                function_name,
                setting=setting,
                aws_lambda=Config.aws_lambda,
                test_mode=setting.get("test_mode"),
            )
        return Config.schemas[function_name]
