#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import functools
import logging
import os
import sys
import traceback
import zipfile
from typing import Any, Callable, Dict, Optional

from graphene import ResolveInfo

from silvaengine_utility import Utility

from ..models.place import get_place
from ..types.ai_marketing import CrmUserListType, PresignedUploadUrlType
from .config import Config


def create_listener_info(
    logger: logging.Logger,
    field_name: str,
    setting: Dict[str, Any],
    **kwargs: Dict[str, Any],
) -> ResolveInfo:
    # Minimal example: some parameters can be None if you're only testing
    info = ResolveInfo(
        field_name=field_name,
        field_asts=[],  # or [some_field_node]
        return_type=None,  # e.g., GraphQLString
        parent_type=None,  # e.g., schema.get_type("Query")
        schema=None,  # your GraphQLSchema
        fragments={},
        root_value=None,
        operation=None,
        variable_values={},
        context={
            "setting": setting,
            "endpoint_id": kwargs.get("endpoint_id"),
            "logger": logger,
            "connectionId": kwargs.get("connection_id"),
        },
        path=None,
    )
    return info


def execute_graphql_query(
    logger: logging.Logger,
    endpoint_id: str,
    function_name: str,
    operation_name: str,
    operation_type: str,
    variables: Dict[str, Any],
    setting: Dict[str, Any] = {},
    connection_id: str = None,
) -> Dict[str, Any]:
    schema = Config.fetch_graphql_schema(
        logger, endpoint_id, function_name, setting=setting
    )
    result = Utility.execute_graphql_query(
        logger,
        endpoint_id,
        function_name,
        Utility.generate_graphql_operation(operation_name, operation_type, schema),
        variables,
        setting=setting,
        aws_lambda=Config.aws_lambda,
        connection_id=connection_id,
        test_mode=setting.get("test_mode"),
    )
    return result


def _module_exists(logger: logging.Logger, module_name: str) -> bool:
    """Check if the module exists in the specified path."""
    module_dir = os.path.join(Config.module_extract_path, module_name)
    if os.path.exists(module_dir) and os.path.isdir(module_dir):
        logger.info(f"Module {module_name} found in {Config.module_extract_path}.")
        return True
    logger.info(f"Module {module_name} not found in {Config.module_extract_path}.")
    return False


def _download_and_extract_module(logger: logging.Logger, module_name: str) -> None:
    """Download and extract the module from S3 if not already extracted."""
    key = f"{module_name}.zip"
    zip_path = f"{Config.module_zip_path}/{key}"

    logger.info(
        f"Downloading module from S3: bucket={Config.module_bucket_name}, key={key}"
    )
    Config.aws_s3.download_file(Config.module_bucket_name, key, zip_path)
    logger.info(f"Downloaded {key} from S3 to {zip_path}")

    # Extract the ZIP file
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(Config.module_extract_path)
    logger.info(f"Extracted module to {Config.module_extract_path}")


def _get_class_object(
    logger: logging.Logger, module_name: str, class_name: str, **setting: Dict[str, Any]
) -> Optional[Callable]:
    try:
        if not _module_exists(logger, module_name):
            # Download and extract the module if it doesn't exist
            _download_and_extract_module(logger, module_name)

        # Add the extracted module to sys.path
        module_path = f"{Config.module_extract_path}/{module_name}"
        if module_path not in sys.path:
            sys.path.append(module_path)

        _class = getattr(__import__(module_name), class_name)

        return _class(
            logger,
            **Utility.json_loads(Utility.json_dumps(setting)),
        )
    except Exception as e:
        log = traceback.format_exc()
        logger.error(log)
        raise e


def get_crm_connector(logger: logging.Logger, setting: Dict[str, Any]) -> Optional[Any]:
    if "crm_connector_config" in setting:
        crm_connector = _get_class_object(
            logger,
            setting["crm_connector_config"]["module_name"],
            setting["crm_connector_config"]["class_name"],
            **setting["crm_connector_config"]["setting"],
        )
        return crm_connector


def put_message_to_target(
    logger: logging.Logger,
    endpoint_id: str,
    data_type: str,
    message: Dict[str, Any],
    setting: Dict[str, Any] = {},
) -> Any:
    """
    Sends messages to the target system using GraphQL mutation.

    Args:
        logger: Logger instance for logging operations
        endpoint_id: Identifier for the endpoint
        data_type: Type of data being sent
        messages: Dictionary containing message data
        setting: Configuration settings with data_mapping and target info

    Returns:
        The message_group_id returned from the GraphQL mutation
    """
    # Prepare variables for GraphQL mutation
    tx_type = setting.get("data_mapping", {}).get(data_type)
    target = setting.get("target")
    if tx_type is None or target is None:
        return None

    variables = {
        "txType": tx_type,
        "source": "sqs",
        "target": target,
        "messages": [message],
    }

    # Execute GraphQL mutation and return the result
    return Utility.execute_graphql_query(
        logger,
        endpoint_id,
        "datawald_interface_graphql",
        "putMessages",
        "Mutation",
        variables,
        setting=setting,
    )


def data_sync_decorator(original_function):
    @functools.wraps(original_function)
    def wrapper_function(*args, **kwargs):

        # Extract endpoint_id from kwargs
        endpoint_id = kwargs.get("endpoint_id")
        if endpoint_id is not None:
            # Log the endpoint ID
            logging.info(f"Endpoint ID: {endpoint_id}")

        # Execute the original function
        result = original_function(*args, **kwargs)

        # Extract data type and message from the result
        # TODO: add the logic to sync data to other data sources
        data_type = type(result).__name__
        message = result.__dict__ if hasattr(result, "__dict__") else result

        # Log information about the function execution
        args[0].context.get("logger").info(
            f"Function {original_function.__name__} returned data of type: {data_type}"
        )
        args[0].context.get("logger").info(
            f"Function {original_function.__name__} messages: {Utility.json_dumps(message)}"
        )

        # Send the message to the target system
        # put_message_to_target(
        #     args[0].context.get("logger"),
        #     endpoint_id,
        #     data_type,
        #     message,
        #     setting=args[0].context.get("setting"),
        # )

        # Return the original function's result
        return result

    return wrapper_function


def resolve_crm_user_list(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CrmUserListType:
    place = get_place(kwargs.get("region"), kwargs.get("place_uuid"))
    crm_user_list = Config.crm_connector.lookup_crm_user_list(
        info.context["logger"],
        **{
            "address": place.address,
            "page_size": kwargs.get("page_size", 100),
            "page_number": kwargs.get("page_number", 0),
        },
    )

    return CrmUserListType(
        page_size=crm_user_list["page_size"],
        page_number=crm_user_list["page_number"],
        total=crm_user_list["total"],
        crm_user_list=[
            CrmUserType(**crm_user) for crm_user in crm_user_list["crm_user_list"]
        ],
    )


def resolve_presigned_upload_url(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> PresignedUploadUrlType:
    # bucket_name, object_key, expiration=3600):
    """
    Generate a presigned URL to upload a file to an S3 bucket.

    :param bucket_name: Name of the S3 bucket.
    :param object_key: Name of the file to be uploaded (object key).
    :param expiration: Time in seconds for the presigned URL to remain valid.
    :return: Presigned URL as a string.
    """
    bucket_name = info.context["setting"].get("aws_s3_bucket")
    object_key = kwargs.get("object_key")
    expiration = info.context["setting"].get("expiration", 3600)  # Default to 1 hour

    # Generate the presigned URL for put_object
    try:
        response = Config.aws_s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=expiration,
            HttpMethod="PUT",
        )

        return PresignedUploadUrlType(
            url=response,
            object_key=object_key,
            expiration=expiration,
        )
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").error(log)
        raise e
