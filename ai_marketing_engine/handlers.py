#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
import traceback
from typing import Any, Dict

import pendulum
from graphene import ResolveInfo
from tenacity import retry, stop_after_attempt, wait_exponential

from silvaengine_dynamodb_base import (
    delete_decorator,
    insert_update_decorator,
    monitor_decorator,
    resolve_list_decorator,
)
from silvaengine_utility import Utility

from .models import (
    CompanyContactProfileModel,
    CompanyContactRequestModel,
    CompanyCorporationProfileModel,
    ContactChatbotHistoryModel,
    ContactProfileModel,
    CorporationPlaceModel,
    CorporationProfileModel,
    PlaceModel,
    QuestionCriteriaModel,
    QuestionModel,
    UtmTagDataCollectionModel,
)
from .types import (
    CompanyContactProfileListType,
    CompanyContactProfileType,
    CompanyContactRequestListType,
    CompanyContactRequestType,
    CompanyCorporationProfileListType,
    CompanyCorporationProfileType,
    ContactChatbotHistoryListType,
    ContactChatbotHistoryType,
    ContactProfileListType,
    ContactProfileType,
    CorporationPlaceListType,
    CorporationPlaceType,
    CorporationProfileListType,
    CorporationProfileType,
    PlaceListType,
    PlaceType,
    QuestionCriteriaListType,
    QuestionCriteriaType,
    QuestionListType,
    QuestionType,
    UtmTagDataCollectionListType,
    UtmTagDataCollectionType,
)


def handlers_init(logger: logging.Logger, **setting: Dict[str, Any]) -> None:
    try:
        pass
    except Exception as e:
        log = traceback.format_exc()
        logger.error(log)
        raise e


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_question(endpoint_id: str, question_uuid: str) -> QuestionModel:
    return QuestionModel.get(endpoint_id, question_uuid)


def get_question_count(endpoint_id: str, question_uuid: str) -> int:
    return QuestionModel.count(
        endpoint_id, QuestionModel.question_uuid == question_uuid
    )


def get_question_type(info: ResolveInfo, question: QuestionModel) -> QuestionType:
    try:
        question_criteria = _get_question_criteria(
            question.endpoint_id, question.question_group
        )
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    question = question.__dict__["attribute_values"]
    question["priority"] = question_criteria["weight"] * 10 + question["priority"]
    return QuestionType(**Utility.json_loads(Utility.json_dumps(question)))


def resolve_question_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> QuestionType:
    return get_question_type(
        info,
        get_question(info.context["endpoint_id"], kwargs.get("question_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "question_uuid"],
    list_type_class=QuestionListType,
    type_funct=get_question_type,
)
def resolve_question_list_handler(info: ResolveInfo, **kwargs: Dict[str, Any]) -> Any:
    endpoint_id = info.context["endpoint_id"]
    question_groups = kwargs.get("question_groups")
    question = kwargs.get("question")
    attribute = kwargs.get("attribute")

    args = []
    inquiry_funct = QuestionModel.scan
    count_funct = QuestionModel.count
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = QuestionModel.query

    the_filters = None  # We can add filters for the query.
    if question_groups:
        the_filters &= QuestionModel.question_group.is_in(*question_groups)
    if question:
        the_filters &= QuestionModel.question.contains(question)
    if attribute:
        the_filters &= QuestionModel.attribute.contains(attribute)
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "question_uuid",
    },
    model_funct=get_question,
    count_funct=get_question_count,
    type_funct=get_question_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_question_handler(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    question_uuid = kwargs.get("question_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "question_group": kwargs["question_group"],
            "question": kwargs["question"],
            "priority": kwargs["priority"],
            "attribute": kwargs["attribute"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        for key in ["option_values", "condition"]:
            if key in kwargs:
                cols[key] = kwargs[key]
        QuestionModel(
            endpoint_id,
            question_uuid,
            **cols,
        ).save()
        return

    question = kwargs.get("entity")
    actions = [
        QuestionModel.updated_by.set(kwargs["updated_by"]),
        QuestionModel.updated_at.set(pendulum.now("UTC")),
    ]

    # Map of kwargs keys to QuestionModel attributes
    field_map = {
        "question_group": QuestionModel.question_group,
        "question": QuestionModel.question,
        "priority": QuestionModel.priority,
        "attribute": QuestionModel.attribute,
        "option_values": QuestionModel.option_values,
        "condition": QuestionModel.condition,
    }

    # Add actions dynamically based on the presence of keys in kwargs
    for key, field in field_map.items():
        if key in kwargs:  # Check if the key exists in kwargs
            actions.append(field.set(None if kwargs[key] == "null" else kwargs[key]))

    # Update the question
    question.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "question_uuid",
    },
    model_funct=get_question,
)
def delete_question_handler(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_question_criteria(
    endpoint_id: str, question_group: str
) -> QuestionCriteriaModel:
    return QuestionCriteriaModel.get(endpoint_id, question_group)


def get_question_criteria_count(endpoint_id: str, question_group: str) -> int:
    return QuestionCriteriaModel.count(
        endpoint_id, QuestionCriteriaModel.question_group == question_group
    )


def _get_question_criteria(endpoint_id: str, question_group: str) -> Dict[str, Any]:
    question_criteria = get_question_criteria(endpoint_id, question_group)
    return {
        "endpoint_id": question_criteria.endpoint_id,
        "question_group": question_criteria.question_group,
        "region": question_criteria.region,
        "question_criteria": question_criteria.question_criteria,
        "weight": question_criteria.weight,
    }


def get_question_criteria_type(
    info: ResolveInfo, question_criteria: QuestionCriteriaModel
) -> QuestionCriteriaType:
    question_criteria = question_criteria.__dict__["attribute_values"]
    return QuestionCriteriaType(
        **Utility.json_loads(Utility.json_dumps(question_criteria))
    )


def resolve_question_criteria_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> QuestionCriteriaType:
    return get_question_criteria_type(
        info,
        get_question_criteria(
            info.context["endpoint_id"], kwargs.get("question_group")
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "question_group"],
    list_type_class=QuestionCriteriaListType,
    type_funct=get_question_criteria_type,
)
def resolve_question_criteria_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    endpoint_id = info.context["endpoint_id"]
    region = kwargs.get("region")
    question_criteria = kwargs.get("question_criteria")

    args = []
    inquiry_funct = QuestionCriteriaModel.scan
    count_funct = QuestionCriteriaModel.count
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = QuestionCriteriaModel.query

    the_filters = None  # We can add filters for the query.
    if region:
        the_filters &= QuestionCriteriaModel.region == region
    if question_criteria:
        if question_criteria.get("place_types"):
            the_filters &= QuestionCriteriaModel.question_criteria[
                "place_type"
            ].exists()
            the_filters &= QuestionCriteriaModel.question_criteria["place_type"].is_in(
                *question_criteria["place_types"]
            )
        if question_criteria.get("corporation_type"):
            the_filters &= QuestionCriteriaModel.question_criteria[
                "corporation_type"
            ].exists()
            the_filters &= (
                QuestionCriteriaModel.question_criteria["corporation_type"]
                == question_criteria["corporation_type"]
            )
        if question_criteria.get("corporation_categories"):
            the_filters &= QuestionCriteriaModel.question_criteria[
                "corporation_category"
            ].exists()
            the_filters &= QuestionCriteriaModel.question_criteria[
                "corporation_category"
            ].is_in(*question_criteria["corporation_categories"])
        if question_criteria.get("utm_tag_name"):
            the_filters &= QuestionCriteriaModel.question_criteria[
                "utm_tag_name"
            ].exists()
            the_filters &= (
                QuestionCriteriaModel.question_criteria["utm_tag_name"]
                == question_criteria["utm_tag_name"]
            )
        if question_criteria.get("corporation_uuid"):
            the_filters &= QuestionCriteriaModel.question_criteria[
                "corporation_uuids"
            ].exists()
            the_filters &= QuestionCriteriaModel.question_criteria[
                "corporation_uuids"
            ].contains(question_criteria["corporation_uuid"])
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "question_group",
    },
    range_key_required=True,
    model_funct=get_question_criteria,
    count_funct=get_question_criteria_count,
    type_funct=get_question_criteria_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_question_criteria_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    question_group = kwargs.get("question_group")
    if kwargs.get("entity") is None:
        cols = {
            "region": kwargs["region"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        for key in ["question_criteria", "weight"]:
            if key in kwargs:
                cols[key] = kwargs[key]
        QuestionCriteriaModel(endpoint_id, question_group, **cols).save()
        return

    question_criteria = kwargs.get("entity")
    actions = [
        QuestionCriteriaModel.updated_by.set(kwargs["updated_by"]),
        QuestionCriteriaModel.updated_at.set(pendulum.now("UTC")),
    ]

    # Map of kwargs keys to QuestionCriteriaModel attributes
    field_map = {
        "region": QuestionCriteriaModel.region,
        "question_criteria": QuestionCriteriaModel.question_criteria,
        "weight": QuestionCriteriaModel.weight,
    }

    # Add actions dynamically based on the presence of keys in kwargs
    for key, field in field_map.items():
        if key in kwargs:  # Check if the key exists in kwargs
            actions.append(field.set(None if kwargs[key] == "null" else kwargs[key]))

    # Update the question criteria
    question_criteria.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "question_group",
    },
    model_funct=get_question_criteria,
)
def delete_question_criteria_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> bool:
    kwargs.get("entity").delete()
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_place(region: str, place_uuid: str) -> PlaceModel:
    return PlaceModel.get(region, place_uuid)


def _get_place(region: str, place_uuid: str) -> Dict[str, Any]:
    place = get_place(region, place_uuid)
    return {
        "region": place.region,
        "place_uuid": place.place_uuid,
        "business_name": place.business_name,
        "latitude": place.latitude,
        "longitude": place.longitude,
        "address": place.address,
        "website": place.website,
        "types": place.types,
    }


def get_place_count(region: str, place_uuid: str) -> int:
    return PlaceModel.count(region, PlaceModel.place_uuid == place_uuid)


def get_place_type(info: ResolveInfo, place: PlaceModel) -> PlaceType:
    place = place.__dict__["attribute_values"]
    return PlaceType(**Utility.json_loads(Utility.json_dumps(place)))


def resolve_place_handler(info: ResolveInfo, **kwargs: Dict[str, Any]) -> PlaceType:
    return get_place_type(
        info,
        get_place(kwargs.get("region"), kwargs.get("place_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["region", "place_uuid"],
    list_type_class=PlaceListType,
    type_funct=get_place_type,
)
def resolve_place_list_handler(info: ResolveInfo, **kwargs: Dict[str, Any]) -> Any:
    region = kwargs.get("region")
    latitude = kwargs.get("latitude")
    longitude = kwargs.get("longitude")
    business_name = kwargs.get("business_name")
    address = kwargs.get("address")
    website = kwargs.get("website")

    args = []
    inquiry_funct = PlaceModel.scan
    count_funct = PlaceModel.count
    if region:
        args = [region, None]
        inquiry_funct = PlaceModel.query

    the_filters = None  # We can add filters for the query.
    if latitude:
        the_filters &= PlaceModel.latitude == latitude
    if longitude:
        the_filters &= PlaceModel.longitude == longitude
    if business_name:
        the_filters &= PlaceModel.business_name.contains(business_name)
    if address:
        the_filters &= PlaceModel.address.contains(address)
    if website:
        the_filters &= PlaceModel.website.contains(website)
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "region",
        "range_key": "place_uuid",
    },
    model_funct=get_place,
    count_funct=get_place_count,
    type_funct=get_place_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_place_handler(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    region = kwargs.get("region")
    place_uuid = kwargs.get("place_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "latitude": kwargs["latitude"],
            "longitude": kwargs["longitude"],
            "business_name": kwargs["business_name"],
            "address": kwargs["address"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        for key in ["phone_number", "types", "website"]:
            if key in kwargs:
                cols[key] = kwargs[key]
        PlaceModel(
            region,
            place_uuid,
            **cols,
        ).save()
        return

    place = kwargs.get("entity")
    actions = [
        PlaceModel.updated_by.set(kwargs["updated_by"]),
        PlaceModel.updated_at.set(pendulum.now("UTC")),
    ]

    # Map of kwargs keys to PlaceModel attributes
    field_map = {
        "latitude": PlaceModel.latitude,
        "longitude": PlaceModel.longitude,
        "business_name": PlaceModel.business_name,
        "address": PlaceModel.address,
        "phone_number": PlaceModel.phone_number,
        "website": PlaceModel.website,
        "types": PlaceModel.types,
    }

    # Add actions dynamically based on the presence of keys in kwargs
    for key, field in field_map.items():
        if key in kwargs:  # Check if the key exists in kwargs
            actions.append(field.set(None if kwargs[key] == "null" else kwargs[key]))

    # Update the place
    place.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "region",
        "range_key": "place_uuid",
    },
    model_funct=get_place,
)
def delete_place_handler(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_contact_profile(place_uuid: str, contact_uuid: str) -> ContactProfileModel:
    return ContactProfileModel.get(place_uuid, contact_uuid)


def _get_contact_profile(place_uuid: str, contact_uuid: str) -> Dict[str, Any]:
    contact_profile = get_contact_profile(place_uuid, contact_uuid)
    return {
        "contact_uuid": contact_profile.contact_uuid,
        "place": _get_place(contact_profile.region, contact_profile.place_uuid),
        "email": contact_profile.email,
        "first_name": contact_profile.first_name,
        "last_name": contact_profile.last_name,
        "corporation_profile": (
            _get_corporation_profile(
                contact_profile.corporation_type, contact_profile.corporation_uuid
            )
            if contact_profile.corporation_type is not None
            and contact_profile.corporation_uuid is not None
            else None
        ),
        "data": contact_profile.data,
    }


def get_contact_profile_count(place_uuid: str, contact_uuid: str) -> int:
    return ContactProfileModel.count(
        place_uuid, ContactProfileModel.contact_uuid == contact_uuid
    )


def get_contact_profile_type(
    info: ResolveInfo, contact_profile: ContactProfileModel
) -> ContactProfileType:
    try:
        place = _get_place(contact_profile.region, contact_profile.place_uuid)
        corporation_profile = None
        if (
            contact_profile.corporation_type is not None
            and contact_profile.corporation_uuid is not None
        ):
            corporation_profile = _get_corporation_profile(
                contact_profile.corporation_type,
                contact_profile.corporation_uuid,
            )
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    contact_profile = contact_profile.__dict__["attribute_values"]
    contact_profile["place"] = place
    contact_profile.pop("region")
    contact_profile.pop("place_uuid")
    if corporation_profile is not None:
        contact_profile["corporation_profile"] = corporation_profile
        contact_profile.pop("corporation_type")
        contact_profile.pop("corporation_uuid")
    return ContactProfileType(**Utility.json_loads(Utility.json_dumps(contact_profile)))


def resolve_contact_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactProfileType:
    return get_contact_profile_type(
        info,
        get_contact_profile(kwargs.get("place_uuid"), kwargs.get("contact_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["place_uuid", "contact_uuid"],
    list_type_class=ContactProfileListType,
    type_funct=get_contact_profile_type,
)
def resolve_contact_profile_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    place_uuid = kwargs.get("place_uuid")
    email = kwargs.get("email")
    regions = kwargs.get("regions")
    first_name = kwargs.get("first_name")
    last_name = kwargs.get("last_name")

    args = []
    inquiry_funct = ContactProfileModel.scan
    count_funct = ContactProfileModel.count
    if place_uuid:
        args = [place_uuid, None]
        inquiry_funct = ContactProfileModel.query

    the_filters = None  # We can add filters for the query.
    if email:
        the_filters &= ContactProfileModel.email.contains(email)
    if regions:
        the_filters &= ContactProfileModel.region.is_in(*regions)
    if first_name:
        the_filters &= ContactProfileModel.first_name.contains(first_name)
    if last_name:
        the_filters &= ContactProfileModel.last_name.contains(last_name)
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "place_uuid",
        "range_key": "contact_uuid",
    },
    model_funct=get_contact_profile,
    count_funct=get_contact_profile_count,
    type_funct=get_contact_profile_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_contact_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    place_uuid = kwargs.get("place_uuid")
    contact_uuid = kwargs.get("contact_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "email": kwargs["email"],
            "region": kwargs["region"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        for key in [
            "first_name",
            "last_name",
            "corporation_type",
            "corporation_uuid",
            "data",
        ]:
            if key in kwargs:
                cols[key] = kwargs[key]
        ContactProfileModel(
            place_uuid,
            contact_uuid,
            **cols,
        ).save()
        return

    contact_profile = kwargs.get("entity")
    actions = [
        ContactProfileModel.updated_by.set(kwargs["updated_by"]),
        ContactProfileModel.updated_at.set(pendulum.now("UTC")),
    ]

    # Map of kwargs keys to ContactProfileModel attributes
    field_map = {
        "email": ContactProfileModel.email,
        "region": ContactProfileModel.region,
        "first_name": ContactProfileModel.first_name,
        "last_name": ContactProfileModel.last_name,
        "data": ContactProfileModel.data,
    }

    # Add actions dynamically based on the presence of keys in kwargs
    for key, field in field_map.items():
        if key in kwargs:  # Check if the key exists in kwargs
            actions.append(field.set(None if kwargs[key] == "null" else kwargs[key]))

    # Handle corporation fields separately due to their special logic
    if (
        kwargs.get("corporation_type") is not None
        and kwargs.get("corporation_uuid") is not None
    ):
        actions.append(
            ContactProfileModel.corporation_type.set(kwargs.get("corporation_type"))
        )
        actions.append(
            ContactProfileModel.corporation_uuid.set(kwargs.get("corporation_uuid"))
        )
    elif "corporation_type" in kwargs or "corporation_uuid" in kwargs:
        actions.append(ContactProfileModel.corporation_type.remove())
        actions.append(ContactProfileModel.corporation_uuid.remove())

    # Update the contact profile
    contact_profile.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "place_uuid",
        "range_key": "contact_uuid",
    },
    model_funct=get_contact_profile,
)
def delete_contact_profile_handler(info: ResolveInfo, **kwargs: Dict[str, Any]) -> bool:
    kwargs.get("entity").delete()
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_company_contact_profile(
    endpoint_id: str, contact_uuid: str
) -> CompanyContactProfileModel:
    return CompanyContactProfileModel.get(endpoint_id, contact_uuid)


def _get_company_contact_profile(endpoint_id: str, contact_uuid: str) -> Dict[str, Any]:
    company_contact_profile = get_company_contact_profile(endpoint_id, contact_uuid)
    return {
        "endpoint_id": company_contact_profile.endpoint_id,
        "contact_profile": _get_contact_profile(
            company_contact_profile.place_uuid,
            company_contact_profile.contact_uuid,
        ),
        "email": company_contact_profile.email,
        "data": company_contact_profile.data,
    }


def get_company_contact_profile_count(endpoint_id: str, contact_uuid: str) -> int:
    return CompanyContactProfileModel.count(
        endpoint_id, CompanyContactProfileModel.contact_uuid == contact_uuid
    )


def get_company_contact_profile_type(
    info: ResolveInfo,
    company_contact_profile: CompanyContactProfileModel,
) -> CompanyContactProfileType:
    try:
        contact_profile = _get_contact_profile(
            company_contact_profile.place_uuid,
            company_contact_profile.contact_uuid,
        )
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    company_contact_profile = company_contact_profile.__dict__["attribute_values"]
    company_contact_profile["contact_profile"] = contact_profile
    company_contact_profile.pop("place_uuid")
    company_contact_profile.pop("contact_uuid")
    return CompanyContactProfileType(
        **Utility.json_loads(Utility.json_dumps(company_contact_profile))
    )


def resolve_company_contact_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CompanyContactProfileType:
    return get_company_contact_profile_type(
        info,
        get_company_contact_profile(
            info.context["endpoint_id"], kwargs.get("contact_uuid")
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "contact_uuid", "email"],
    list_type_class=CompanyContactProfileListType,
    type_funct=get_company_contact_profile_type,
)
def resolve_company_contact_profile_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    endpoint_id = info.context["endpoint_id"]
    email = kwargs.get("email")
    place_uuid = kwargs.get("place_uuid")
    corporation_types = kwargs.get("corporation_types")

    args = []
    inquiry_funct = CompanyContactProfileModel.scan
    count_funct = CompanyContactProfileModel.count
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = CompanyContactProfileModel.query
        if email:
            inquiry_funct = CompanyContactProfileModel.email_index.query
            args[1] = CompanyContactProfileModel.email == email
            count_funct = CompanyContactProfileModel.email_index.count

    the_filters = None  # We can add filters for the query.
    if place_uuid:
        the_filters &= CompanyContactProfileModel.place_uuid == place_uuid
    if corporation_types:
        the_filters &= CompanyContactProfileModel.corporation_type.is_in(
            *corporation_types
        )
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "contact_uuid",
    },
    range_key_required=True,
    model_funct=get_company_contact_profile,
    count_funct=get_company_contact_profile_count,
    type_funct=get_company_contact_profile_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_company_contact_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    contact_uuid = kwargs.get("contact_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "email": kwargs["email"],
            "place_uuid": kwargs["place_uuid"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        if kwargs.get("data") is not None:
            cols["data"] = kwargs["data"]
        CompanyContactProfileModel(
            endpoint_id,
            contact_uuid,
            **cols,
        ).save()
        return

    company_contact_profile = kwargs.get("entity")
    actions = [
        CompanyContactProfileModel.updated_by.set(kwargs.get("updated_by")),
        CompanyContactProfileModel.updated_at.set(pendulum.now("UTC")),
    ]
    if kwargs.get("data") is not None:
        actions.append(CompanyContactProfileModel.data.set(kwargs.get("data")))
    company_contact_profile.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "contact_uuid",
    },
    model_funct=get_company_contact_profile,
)
def delete_company_contact_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> bool:
    kwargs.get("entity").delete()
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_company_contact_request(
    endpoint_id: str, request_uuid: str
) -> CompanyContactRequestModel:
    return CompanyContactRequestModel.get(endpoint_id, request_uuid)


def get_company_contact_request_count(endpoint_id: str, request_uuid: str) -> int:
    return CompanyContactRequestModel.count(
        endpoint_id, CompanyContactRequestModel.request_uuid == request_uuid
    )


def get_company_contact_request_type(
    info: ResolveInfo, company_contact_request: CompanyContactRequestModel
) -> CompanyContactRequestType:
    try:
        company_contact_profile = _get_company_contact_profile(
            company_contact_request.endpoint_id, company_contact_request.contact_uuid
        )
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    company_contact_request = company_contact_request.__dict__["attribute_values"]
    company_contact_request["company_contact_profile"] = company_contact_profile
    company_contact_request.pop("endpoint_id")
    company_contact_request.pop("contact_uuid")
    return CompanyContactRequestType(
        **Utility.json_loads(Utility.json_dumps(company_contact_request))
    )


def resolve_company_contact_request_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CompanyContactRequestType:
    return get_company_contact_request_type(
        info,
        get_company_contact_request(
            kwargs.get("endpoint_id"), kwargs.get("request_uuid")
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "request_uuid", "contact_uuid"],
    list_type_class=CompanyContactRequestListType,
    type_funct=get_company_contact_request_type,
)
def resolve_company_contact_request_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    contact_uuid = kwargs.get("contact_uuid")
    endpoint_id = info.context["endpoint_id"]
    request_title = kwargs.get("request_title")
    request_detail = kwargs.get("request_detail")

    args = []
    inquiry_funct = CompanyContactRequestModel.scan
    count_funct = CompanyContactRequestModel.count
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = CompanyContactRequestModel.query
        if contact_uuid:
            inquiry_funct = CompanyContactRequestModel.contact_uuid_index.query
            args[1] = CompanyContactRequestModel.contact_uuid == contact_uuid
            count_funct = CompanyContactRequestModel.contact_uuid_index.count

    the_filters = None  # We can add filters for the query.
    if request_title:
        the_filters &= CompanyContactRequestModel.request_title.contains(request_title)
    if request_detail:
        the_filters &= CompanyContactRequestModel.request_detail.contains(
            request_detail
        )
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "request_uuid",
    },
    model_funct=get_company_contact_request,
    count_funct=get_company_contact_request_count,
    type_funct=get_company_contact_request_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_company_contact_request_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    request_uuid = kwargs.get("request_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "contact_uuid": kwargs["contact_uuid"],
            "request_title": kwargs["request_title"],
            "request_detail": kwargs["request_detail"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        CompanyContactRequestModel(
            endpoint_id,
            request_uuid,
            **cols,
        ).save()
        return

    company_contact_request = kwargs.get("entity")
    actions = [
        CompanyContactRequestModel.updated_by.set(kwargs["updated_by"]),
        CompanyContactRequestModel.updated_at.set(pendulum.now("UTC")),
    ]
    if kwargs.get("request_title") is not None:
        actions.append(
            CompanyContactRequestModel.request_title.set(kwargs["request_title"])
        )
    if kwargs.get("request_detail") is not None:
        actions.append(
            CompanyContactRequestModel.request_detail.set(kwargs["request_detail"])
        )

    company_contact_request.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "request_uuid",
    },
    model_funct=get_company_contact_request,
)
def delete_company_contact_request_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> bool:
    kwargs.get("entity").delete()
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_corporation_profile(
    corporation_type: str, corporation_uuid: str
) -> CorporationProfileModel:
    return CorporationProfileModel.get(corporation_type, corporation_uuid)


def _get_corporation_profile(
    corporation_type: str, corporation_uuid: str
) -> Dict[str, Any]:
    corporation_profile = get_corporation_profile(corporation_type, corporation_uuid)
    return {
        "corporation_type": corporation_profile.corporation_type,
        "corporation_uuid": corporation_profile.corporation_uuid,
        "external_id": corporation_profile.external_id,
        "business_name": corporation_profile.business_name,
        "categories": corporation_profile.categories,
        "address": corporation_profile.address,
        "data": corporation_profile.data,
    }


def get_corporation_profile_count(corporation_type: str, corporation_uuid: str) -> int:
    return CorporationProfileModel.count(
        corporation_type, CorporationProfileModel.corporation_uuid == corporation_uuid
    )


def get_corporation_profile_type(
    info: ResolveInfo, corporation_profile: CorporationProfileModel
) -> CorporationProfileType:
    corporation_profile = corporation_profile.__dict__["attribute_values"]
    return CorporationProfileType(
        **Utility.json_loads(Utility.json_dumps(corporation_profile))
    )


def resolve_corporation_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CorporationProfileType:
    return get_corporation_profile_type(
        info,
        get_corporation_profile(
            kwargs.get("corporation_type"), kwargs.get("corporation_uuid")
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["corporation_type", "corporation_uuid", "external_id"],
    list_type_class=CorporationProfileListType,
    type_funct=get_corporation_profile_type,
)
def resolve_corporation_profile_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    corporation_type = kwargs.get("corporation_type")
    external_id = kwargs.get("external_id")
    business_name = kwargs.get("business_name")
    category = kwargs.get("category")

    args = []
    inquiry_funct = CorporationProfileModel.scan
    count_funct = CorporationProfileModel.count
    if corporation_type:
        args = [corporation_type, None]
        inquiry_funct = CorporationProfileModel.query
        if external_id:
            inquiry_funct = CorporationProfileModel.external_id_index.query
            args[1] = CorporationProfileModel.external_id == external_id
            count_funct = CorporationProfileModel.external_id_index.count

    the_filters = None  # We can add filters for the query.
    if business_name:
        the_filters &= CorporationProfileModel.business_name == business_name
    if category:
        the_filters &= CorporationProfileModel.categories.contains(category)
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "corporation_type",
        "range_key": "corporation_uuid",
    },
    model_funct=get_corporation_profile,
    count_funct=get_corporation_profile_count,
    type_funct=get_corporation_profile_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_corporation_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    corporation_type = kwargs.get("corporation_type")
    corporation_uuid = kwargs.get("corporation_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "external_id": kwargs["external_id"],
            "business_name": kwargs["business_name"],
            "address": kwargs["address"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        for key in ["categories", "data"]:
            if key in kwargs:
                cols[key] = kwargs[key]
        CorporationProfileModel(
            corporation_type,
            corporation_uuid,
            **cols,
        ).save()
        return

    corporation_profile = kwargs.get("entity")
    actions = [
        CorporationProfileModel.updated_by.set(kwargs["updated_by"]),
        CorporationProfileModel.updated_at.set(pendulum.now("UTC")),
    ]

    # Map of kwargs keys to CorporationProfileModel attributes
    field_map = {
        "external_id": CorporationProfileModel.external_id,
        "business_name": CorporationProfileModel.business_name,
        "categories": CorporationProfileModel.categories,
        "address": CorporationProfileModel.address,
        "data": CorporationProfileModel.data,
    }

    # Add actions dynamically based on the presence of keys in kwargs
    for key, field in field_map.items():
        if key in kwargs:  # Check if the key exists in kwargs
            actions.append(field.set(None if kwargs[key] == "null" else kwargs[key]))

    corporation_profile.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "corporation_type",
        "range_key": "corporation_uuid",
    },
    model_funct=get_corporation_profile,
)
def delete_corporation_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> bool:
    kwargs.get("entity").delete()
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_corporation_place(region: str, corporation_uuid: str) -> CorporationPlaceModel:
    return CorporationPlaceModel.get(region, corporation_uuid)


def get_corporation_place_count(region: str, corporation_uuid: str) -> int:
    return CorporationPlaceModel.count(
        region,
        CorporationPlaceModel.corporation_uuid == corporation_uuid,
    )


def get_corporation_place_type(
    info: ResolveInfo, corporation_place: CorporationPlaceModel
) -> CorporationPlaceType:
    try:
        corporation_profile = _get_corporation_profile(
            corporation_place.corporation_type,
            corporation_place.corporation_uuid,
        )
        place = _get_place(
            corporation_place.region,
            corporation_place.place_uuid,
        )
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    corporation_place = corporation_place.__dict__["attribute_values"]
    corporation_place["corporation_profile"] = corporation_profile
    corporation_place.pop("corporation_type")
    corporation_place.pop("corporation_uuid")
    corporation_place["place"] = place
    corporation_place.pop("region")
    corporation_place.pop("place_uuid")
    return CorporationPlaceType(
        **Utility.json_loads(Utility.json_dumps(corporation_place))
    )


def resolve_corporation_place_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CorporationPlaceType:
    return get_corporation_place_type(
        info,
        get_corporation_place(kwargs.get("region"), kwargs.get("corporation_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["region", "corporation_uuid", "place_uuid"],
    list_type_class=CorporationPlaceListType,
    type_funct=get_corporation_place_type,
)
def resolve_corporation_place_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    region = kwargs.get("region")
    place_uuid = kwargs.get("place_uuid")
    corporation_types = kwargs.get("corporation_types")

    args = []
    inquiry_funct = CorporationPlaceModel.scan
    count_funct = CorporationPlaceModel.count
    if region:
        args = [region, None]
        inquiry_funct = CorporationPlaceModel.query
        if place_uuid:
            inquiry_funct = CorporationPlaceModel.place_uuid_index.query
            args[1] = CorporationPlaceModel.place_uuid == place_uuid
            count_funct = CorporationPlaceModel.place_uuid_index.count

    the_filters = None  # We can add filters for the query.
    if corporation_types:
        the_filters &= CorporationPlaceModel.corporation_type.is_in(*corporation_types)
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "region",
        "range_key": "corporation_uuid",
    },
    range_key_required=True,
    model_funct=get_corporation_place,
    count_funct=get_corporation_place_count,
    type_funct=get_corporation_place_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_corporation_place_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    region = kwargs.get("region")
    corporation_uuid = kwargs.get("corporation_uuid")
    if kwargs.get("entity") is None:
        CorporationPlaceModel(
            region,
            corporation_uuid,
            **{
                "place_uuid": kwargs["place_uuid"],
                "corporation_type": kwargs["corporation_type"],
                "updated_by": kwargs["updated_by"],
                "created_at": pendulum.now("UTC"),
                "updated_at": pendulum.now("UTC"),
            },
        ).save()
        return

    corporation_place = kwargs.get("entity")
    actions = [
        CorporationPlaceModel.updated_by.set(kwargs.get("updated_by")),
        CorporationPlaceModel.updated_at.set(pendulum.now("UTC")),
    ]
    if kwargs.get("place_uuid") is not None:
        actions.append(CorporationPlaceModel.place_uuid.set(kwargs.get("place_uuid")))
    if kwargs.get("corporation_type") is not None:
        actions.append(
            CorporationPlaceModel.corporation_type.set(kwargs.get("corporation_type"))
        )
    corporation_place.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "region",
        "range_key": "corporation_uuid",
    },
    model_funct=get_corporation_place,
)
def delete_corporation_place_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> bool:
    kwargs.get("entity").delete()
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_company_corporation_profile(
    endpoint_id: str, corporation_uuid: str
) -> CompanyCorporationProfileModel:
    return CompanyCorporationProfileModel.get(endpoint_id, corporation_uuid)


def get_company_corporation_profile_count(
    endpoint_id: str, corporation_uuid: str
) -> int:
    return CompanyCorporationProfileModel.count(
        endpoint_id,
        CompanyCorporationProfileModel.corporation_uuid == corporation_uuid,
    )


def get_company_corporation_profile_type(
    info: ResolveInfo,
    company_corporation_profile: CompanyCorporationProfileModel,
) -> CompanyCorporationProfileType:
    try:
        corporation_profile = _get_corporation_profile(
            company_corporation_profile.corporation_type,
            company_corporation_profile.corporation_uuid,
        )
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    company_corporation_profile = company_corporation_profile.__dict__[
        "attribute_values"
    ]
    company_corporation_profile["corporation_profile"] = corporation_profile
    company_corporation_profile.pop("corporation_type")
    company_corporation_profile.pop("corporation_uuid")
    return CompanyCorporationProfileType(
        **Utility.json_loads(Utility.json_dumps(company_corporation_profile))
    )


def resolve_company_corporation_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CompanyCorporationProfileType:
    return get_company_corporation_profile_type(
        info,
        get_company_corporation_profile(
            info.context["endpoint_id"], kwargs.get("corporation_uuid")
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "corporation_uuid", "external_id"],
    list_type_class=CompanyCorporationProfileListType,
    type_funct=get_company_corporation_profile_type,
)
def resolve_company_corporation_profile_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    endpoint_id = info.context["endpoint_id"]
    external_id = kwargs.get("external_id")
    corporation_types = kwargs.get("corporation_types")

    args = []
    inquiry_funct = CompanyCorporationProfileModel.scan
    count_funct = CompanyCorporationProfileModel.count
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = CompanyCorporationProfileModel.query
        if external_id:
            inquiry_funct = CompanyCorporationProfileModel.external_id_index.query
            args[1] = CompanyCorporationProfileModel.external_id == external_id
            count_funct = CompanyCorporationProfileModel.external_id_index.count

    the_filters = None  # We can add filters for the query.
    if corporation_types:
        the_filters &= CompanyCorporationProfileModel.corporation_type.is_in(
            *corporation_types
        )
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "corporation_uuid",
    },
    range_key_required=True,
    model_funct=get_company_corporation_profile,
    count_funct=get_company_corporation_profile_count,
    type_funct=get_company_corporation_profile_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_company_corporation_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    corporation_uuid = kwargs.get("corporation_uuid")
    if kwargs.get("entity") is None:
        cols = {
            "external_id": kwargs["external_id"],
            "corporation_type": kwargs["corporation_type"],
            "updated_by": kwargs["updated_by"],
            "created_at": pendulum.now("UTC"),
            "updated_at": pendulum.now("UTC"),
        }
        if kwargs.get("data"):
            cols["data"] = kwargs.get("data")
        CompanyCorporationProfileModel(
            endpoint_id,
            corporation_uuid,
            **cols,
        ).save()
        return

    company_corporation_profile = kwargs.get("entity")
    actions = [
        CompanyCorporationProfileModel.updated_by.set(kwargs.get("updated_by")),
        CompanyCorporationProfileModel.updated_at.set(pendulum.now("UTC")),
    ]
    if kwargs.get("data"):
        actions.append(CompanyCorporationProfileModel.data.set(kwargs.get("data")))
    company_corporation_profile.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "corporation_uuid",
    },
    model_funct=get_company_corporation_profile,
)
def delete_company_corporation_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> bool:
    kwargs.get("entity").delete()
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_contact_chatbot_history(
    endpoint_id: str, timestamp: str
) -> ContactChatbotHistoryModel:
    return ContactChatbotHistoryModel.get(endpoint_id, timestamp)


def get_contact_chatbot_history_count(endpoint_id: str, timestamp: str) -> int:
    return ContactChatbotHistoryModel.count(
        endpoint_id,
        ContactChatbotHistoryModel.timestamp == timestamp,
    )


def get_contact_chatbot_history_type(
    info: ResolveInfo, contact_chatbot_history: ContactChatbotHistoryModel
) -> ContactChatbotHistoryType:
    contact_chatbot_history = contact_chatbot_history.__dict__["attribute_values"]
    return ContactChatbotHistoryType(
        **Utility.json_loads(Utility.json_dumps(contact_chatbot_history))
    )


def resolve_contact_chatbot_history_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> ContactChatbotHistoryType:
    return get_contact_chatbot_history_type(
        info,
        get_contact_chatbot_history(
            info.context["endpoint_id"], kwargs.get("timestamp")
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "timestamp", "contact_uuid"],
    list_type_class=ContactChatbotHistoryListType,
    type_funct=get_contact_chatbot_history_type,
)
def resolve_contact_chatbot_history_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    endpoint_id = info.context["endpoint_id"]
    contact_uuid = kwargs.get("contact_uuid")
    place_uuids = kwargs.get("place_uuids")
    regions = kwargs.get("regions")

    args = []
    inquiry_funct = ContactChatbotHistoryModel.scan
    count_funct = ContactChatbotHistoryModel.count
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = ContactChatbotHistoryModel.query
        if contact_uuid:
            inquiry_funct = ContactChatbotHistoryModel.contact_uuid_index.query
            args[1] = ContactChatbotHistoryModel.contact_uuid == contact_uuid
            count_funct = ContactChatbotHistoryModel.contact_uuid_index.count

    the_filters = None  # We can add filters for the query.
    if place_uuids:
        the_filters &= ContactChatbotHistoryModel.place_uuid.is_in(*place_uuids)
    if regions:
        the_filters &= ContactChatbotHistoryModel.region.is_in(*regions)
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "timestamp",
    },
    range_key_required=True,
    model_funct=get_contact_chatbot_history,
    count_funct=get_contact_chatbot_history_count,
    type_funct=get_contact_chatbot_history_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_contact_chatbot_history_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    timestamp = kwargs.get("timestamp")
    if kwargs.get("entity") is None:
        ContactChatbotHistoryModel(
            endpoint_id,
            timestamp,
            **{
                "contact_uuid": kwargs["contact_uuid"],
                "place_uuid": kwargs["place_uuid"],
                "region": kwargs["region"],
                "assistant_id": kwargs["assistant_id"],
                "thread_id": kwargs["thread_id"],
            },
        ).save()
        return

    return


@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "timestamp",
    },
    model_funct=get_contact_chatbot_history,
)
def delete_contact_chatbot_history_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> bool:
    kwargs.get("entity").delete()
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_utm_tag_data_collection(
    endpoint_id: str, collection_uuid: str
) -> UtmTagDataCollectionModel:
    return UtmTagDataCollectionModel.get(endpoint_id, collection_uuid)


def get_utm_tag_data_collection_count(endpoint_id: str, collection_uuid: str) -> int:
    return UtmTagDataCollectionModel.count(
        endpoint_id,
        UtmTagDataCollectionModel.collection_uuid == collection_uuid,
    )


def get_utm_tag_data_collection_type(
    info: ResolveInfo, utm_tag_data_collection: UtmTagDataCollectionModel
) -> UtmTagDataCollectionType:
    try:
        place = _get_place(
            utm_tag_data_collection.region, utm_tag_data_collection.place_uuid
        )

        contact_profile = None
        results = ContactProfileModel.query(
            place["place_uuid"],
            ContactProfileModel.contact_uuid == utm_tag_data_collection.contact_uuid,
        )
        results = [result for result in results]
        if len(results) > 0:
            contact_place = results[0]
            contact_profile = _get_contact_profile(
                contact_place.place_uuid, utm_tag_data_collection.contact_uuid
            )
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    utm_tag_data_collection = utm_tag_data_collection.__dict__["attribute_values"]
    utm_tag_data_collection["place"] = place
    utm_tag_data_collection.pop("region")
    utm_tag_data_collection.pop("place_uuid")
    utm_tag_data_collection["contact_profile"] = contact_profile
    utm_tag_data_collection.pop("contact_uuid")
    return UtmTagDataCollectionType(
        **Utility.json_loads(Utility.json_dumps(utm_tag_data_collection))
    )


def resolve_utm_tag_data_collection_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> UtmTagDataCollectionType:
    return get_utm_tag_data_collection_type(
        info,
        get_utm_tag_data_collection(
            info.context["endpoint_id"], kwargs.get("collection_uuid")
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["endpoint_id", "collection_uuid", "tag_name"],
    list_type_class=UtmTagDataCollectionListType,
    type_funct=get_utm_tag_data_collection_type,
)
def resolve_utm_tag_data_collection_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    endpoint_id = info.context["endpoint_id"]
    tag_name = kwargs.get("tag_name")
    place_uuids = kwargs.get("place_uuids")
    contact_uuids = kwargs.get("contact_uuids")
    regions = kwargs.get("regions")
    keyword = kwargs.get("keyword")

    args = []
    inquiry_funct = UtmTagDataCollectionModel.scan
    count_funct = UtmTagDataCollectionModel.count
    if endpoint_id:
        args = [endpoint_id, None]
        inquiry_funct = UtmTagDataCollectionModel.query
        if tag_name:
            inquiry_funct = UtmTagDataCollectionModel.tag_name_index.query
            args[1] = UtmTagDataCollectionModel.tag_name == tag_name
            count_funct = UtmTagDataCollectionModel.tag_name_index.count

    the_filters = None  # We can add filters for the query.
    if place_uuids:
        the_filters &= UtmTagDataCollectionModel.place_uuid.is_in(*place_uuids)
    if contact_uuids:
        the_filters &= UtmTagDataCollectionModel.contact_uuid.is_in(*contact_uuids)
    if regions:
        the_filters &= UtmTagDataCollectionModel.region.is_in(*regions)
    if keyword:
        the_filters &= UtmTagDataCollectionModel.keyword.contains(keyword)
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "collection_uuid",
    },
    model_funct=get_utm_tag_data_collection,
    count_funct=get_utm_tag_data_collection_count,
    type_funct=get_utm_tag_data_collection_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_utm_tag_data_collection_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    endpoint_id = kwargs.get("endpoint_id")
    collection_uuid = kwargs.get("collection_uuid")
    if kwargs.get("entity") is None:
        UtmTagDataCollectionModel(
            endpoint_id,
            collection_uuid,
            **{
                "tag_name": kwargs["tag_name"],
                "place_uuid": kwargs["place_uuid"],
                "contact_uuid": kwargs["contact_uuid"],
                "region": kwargs["region"],
                "keyword": kwargs["keyword"],
                "utm_campaign": kwargs["utm_campaign"],
                "utm_content": kwargs["utm_content"],
                "utm_medium": kwargs["utm_medium"],
                "utm_source": kwargs["utm_source"],
                "utm_term": kwargs["utm_term"],
                "created_at": pendulum.now("UTC"),
            },
        ).save()
        return

    return


@delete_decorator(
    keys={
        "hash_key": "endpoint_id",
        "range_key": "collection_uuid",
    },
    model_funct=get_utm_tag_data_collection,
)
def delete_utm_tag_data_collection_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> bool:
    kwargs.get("entity").delete()
    return True
