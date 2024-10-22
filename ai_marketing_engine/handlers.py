#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
import traceback
from typing import Any, Dict

import pendulum
from graphene import ResolveInfo
from silvaengine_dynamodb_base import (
    delete_decorator,
    insert_update_decorator,
    monitor_decorator,
    resolve_list_decorator,
)
from silvaengine_utility import Utility
from tenacity import retry, stop_after_attempt, wait_exponential

from .models import (
    CorporationPlaceModel,
    CorporationProfileAdditionalDataModel,
    CorporationProfileModel,
    CustomerChatbotHistoryModel,
    CustomerProfileAditionalDataModel,
    CustomerProfileModel,
    PlaceModel,
    QuestionCriteriaModel,
    QuestionModel,
    UtmTagDataCollectionModel,
)
from .types import (
    CorporationPlaceListType,
    CorporationPlaceType,
    CorporationProfileAdditionalDataListType,
    CorporationProfileAdditionalDataType,
    CorporationProfileListType,
    CorporationProfileType,
    CustomerChatbotHistoryListType,
    CustomerChatbotHistoryType,
    CustomerProfileAdditionalDataListType,
    CustomerProfileAdditionalDataType,
    CustomerProfileListType,
    CustomerProfileType,
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
def get_question(company_id: str, question_uuid: str) -> QuestionModel:
    return QuestionModel.get(company_id, question_uuid)


def get_question_count(company_id: str, question_uuid: str) -> int:
    return QuestionModel.count(company_id, QuestionModel.question_uuid == question_uuid)


def get_question_type(info: ResolveInfo, question: QuestionModel) -> QuestionType:
    question = question.__dict__["attribute_values"]
    return QuestionType(**Utility.json_loads(Utility.json_dumps(question)))


def resolve_question_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> QuestionType:
    return get_question_type(
        info,
        get_question(kwargs.get("company_id"), kwargs.get("question_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["company_id", "question_uuid"],
    list_type_class=QuestionListType,
    type_funct=get_question_type,
)
def resolve_question_list_handler(info: ResolveInfo, **kwargs: Dict[str, Any]) -> Any:
    company_id = kwargs.get("company_id")
    question_groups = kwargs.get("question_groups")
    question = kwargs.get("question")
    attribute = kwargs.get("attribute")

    args = []
    inquiry_funct = QuestionModel.scan
    count_funct = QuestionModel.count
    if company_id:
        args = [company_id, None]
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
        "hash_key": "company_id",
        "range_key": "question_uuid",
    },
    model_funct=get_question,
    count_funct=get_question_count,
    type_funct=get_question_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_question_handler(info: ResolveInfo, **kwargs: Dict[str, Any]) -> None:
    company_id = kwargs.get("company_id")
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
        if kwargs.get("option_values") is not None:
            cols["option_values"] = kwargs["option_values"]
        if kwargs.get("condition") is not None:
            cols["condition"] = kwargs["condition"]
        QuestionModel(
            company_id,
            question_uuid,
            **cols,
        ).save()
        return

    question = kwargs.get("entity")
    actions = [
        QuestionModel.updated_by.set(kwargs.get("updated_by")),
        QuestionModel.updated_at.set(pendulum.now("UTC")),
    ]
    if kwargs.get("question_group") is not None:
        actions.append(QuestionModel.question_group.set(kwargs.get("question_group")))
    if kwargs.get("question") is not None:
        actions.append(QuestionModel.question.set(kwargs.get("question")))
    if kwargs.get("priority") is not None:
        actions.append(QuestionModel.priority.set(kwargs.get("priority")))
    if kwargs.get("attribute") is not None:
        actions.append(QuestionModel.attribute.set(kwargs.get("attribute")))
    if kwargs.get("option_values") is not None:
        actions.append(QuestionModel.option_values.set(kwargs.get("option_values")))
    if kwargs.get("condition") is not None:
        actions.append(QuestionModel.condition.set(kwargs.get("condition")))
    question.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "company_id",
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
    company_id: str, question_group: str
) -> QuestionCriteriaModel:
    return QuestionCriteriaModel.get(company_id, question_group)


def get_question_criteria_count(company_id: str, question_group: str) -> int:
    return QuestionCriteriaModel.count(
        company_id, QuestionCriteriaModel.question_group == question_group
    )


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
        get_question_criteria(kwargs.get("company_id"), kwargs.get("question_group")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["company_id", "question_group"],
    list_type_class=QuestionCriteriaListType,
    type_funct=get_question_criteria_type,
)
def resolve_question_criteria_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    company_id = kwargs.get("company_id")
    region = kwargs.get("region")
    question_criteria = kwargs.get("question_criteria")

    args = []
    inquiry_funct = QuestionCriteriaModel.scan
    count_funct = QuestionCriteriaModel.count
    if company_id:
        args = [company_id, None]
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
        "hash_key": "company_id",
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
    company_id = kwargs.get("company_id")
    question_group = kwargs.get("question_group")
    cols = {
        "region": kwargs["region"],
        "updated_by": kwargs["updated_by"],
        "created_at": pendulum.now("UTC"),
        "updated_at": pendulum.now("UTC"),
    }
    if kwargs.get("question_criteria") is not None:
        cols["question_criteria"] = kwargs["question_criteria"]
    if kwargs.get("entity") is None:
        QuestionCriteriaModel(company_id, question_group, **cols).save()
        return

    question_criteria = kwargs.get("entity")
    actions = [
        QuestionCriteriaModel.updated_by.set(kwargs.get("updated_by")),
        QuestionCriteriaModel.updated_at.set(pendulum.now("UTC")),
    ]
    if kwargs.get("region") is not None:
        actions.append(QuestionCriteriaModel.region.set(kwargs.get("region")))
    if kwargs.get("question_criteria") is not None:
        actions.append(
            QuestionCriteriaModel.question_criteria.set(kwargs.get("question_criteria"))
        )
    question_criteria.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "company_id",
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


def _get_place(region: str, place_uuid: str) -> PlaceModel:
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
    cols = {
        "latitude": kwargs["latitude"],
        "longitude": kwargs["longitude"],
        "business_name": kwargs["business_name"],
        "address": kwargs["address"],
        "updated_by": kwargs["updated_by"],
        "created_at": pendulum.now("UTC"),
        "updated_at": pendulum.now("UTC"),
    }
    if kwargs.get("phone_number") is not None:
        cols["phone_number"] = kwargs["phone_number"]
    if kwargs.get("types") is not None:
        cols["types"] = kwargs["types"]
    if kwargs.get("entity") is None:
        PlaceModel(
            region,
            place_uuid,
            **cols,
        ).save()
        return

    place = kwargs.get("entity")
    actions = [
        PlaceModel.updated_by.set(kwargs.get("updated_by")),
        PlaceModel.updated_at.set(pendulum.now("UTC")),
    ]
    if kwargs.get("latitude") is not None:
        actions.append(PlaceModel.latitude.set(kwargs.get("latitude")))
    if kwargs.get("longitude") is not None:
        actions.append(PlaceModel.longitude.set(kwargs.get("longitude")))
    if kwargs.get("business_name") is not None:
        actions.append(PlaceModel.business_name.set(kwargs.get("business_name")))
    if kwargs.get("address") is not None:
        actions.append(PlaceModel.address.set(kwargs.get("address")))
    if kwargs.get("phone_number") is not None:
        actions.append(PlaceModel.phone_number.set(kwargs.get("phone_number")))
    if kwargs.get("website") is not None:
        actions.append(PlaceModel.website.set(kwargs.get("website")))
    if kwargs.get("types") is not None:
        actions.append(PlaceModel.types.set(kwargs.get("types")))
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
def get_customer_profile(place_uuid: str, customer_uuid: str) -> CustomerProfileModel:
    return CustomerProfileModel.get(place_uuid, customer_uuid)


def _get_customer_profile(place_uuid: str, customer_uuid: str) -> CustomerProfileModel:
    customer_profile = get_customer_profile(place_uuid, customer_uuid)
    return {
        "customer_uuid": customer_profile.customer_uuid,
        "place": _get_place(customer_profile.region, customer_profile.place_uuid),
        "email": customer_profile.email,
        "first_name": customer_profile.first_name,
        "last_name": customer_profile.last_name,
        "data": customer_profile.data,
    }


def get_customer_profile_count(place_uuid: str, customer_uuid: str) -> int:
    return CustomerProfileModel.count(
        place_uuid, CustomerProfileModel.customer_uuid == customer_uuid
    )


def get_customer_profile_type(
    info: ResolveInfo, customer_profile: CustomerProfileModel
) -> CustomerProfileType:
    try:
        place = _get_place(customer_profile.region, customer_profile.place_uuid)
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    customer_profile = customer_profile.__dict__["attribute_values"]
    customer_profile["place"] = place
    customer_profile.pop("region")
    customer_profile.pop("place_uuid")
    return CustomerProfileType(
        **Utility.json_loads(Utility.json_dumps(customer_profile))
    )


def resolve_customer_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CustomerProfileType:
    return get_customer_profile_type(
        info,
        get_customer_profile(kwargs.get("place_uuid"), kwargs.get("customer_uuid")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["place_uuid", "customer_uuid"],
    list_type_class=CustomerProfileListType,
    type_funct=get_customer_profile_type,
)
def resolve_customer_profile_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    place_uuid = kwargs.get("place_uuid")
    email = kwargs.get("email")
    regions = kwargs.get("regions")
    first_name = kwargs.get("first_name")
    last_name = kwargs.get("last_name")

    args = []
    inquiry_funct = CustomerProfileModel.scan
    count_funct = CustomerProfileModel.count
    if place_uuid:
        args = [place_uuid, None]
        inquiry_funct = CustomerProfileModel.query

    the_filters = None  # We can add filters for the query.
    if email:
        the_filters &= CustomerProfileModel.email.contains(email)
    if regions:
        the_filters &= CustomerProfileModel.region.is_in(*regions)
    if first_name:
        the_filters &= CustomerProfileModel.first_name.contains(first_name)
    if last_name:
        the_filters &= CustomerProfileModel.last_name.contains(last_name)
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "place_uuid",
        "range_key": "customer_uuid",
    },
    model_funct=get_customer_profile,
    count_funct=get_customer_profile_count,
    type_funct=get_customer_profile_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_customer_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    place_uuid = kwargs.get("place_uuid")
    customer_uuid = kwargs.get("customer_uuid")
    if kwargs.get("entity") is None:
        CustomerProfileModel(
            place_uuid,
            customer_uuid,
            **{
                "email": kwargs["email"],
                "region": kwargs["region"],
                "first_name": kwargs["first_name"],
                "last_name": kwargs["last_name"],
                "data": kwargs["data"],
                "updated_by": kwargs["updated_by"],
                "created_at": pendulum.now("UTC"),
                "updated_at": pendulum.now("UTC"),
            },
        ).save()
        return

    customer_profile = kwargs.get("entity")
    actions = [
        CustomerProfileModel.updated_by.set(kwargs.get("updated_by")),
        CustomerProfileModel.updated_at.set(pendulum.now("UTC")),
    ]
    if kwargs.get("email") is not None:
        actions.append(CustomerProfileModel.email.set(kwargs.get("email")))
    if kwargs.get("region") is not None:
        actions.append(CustomerProfileModel.region.set(kwargs.get("region")))
    if kwargs.get("first_name") is not None:
        actions.append(CustomerProfileModel.first_name.set(kwargs.get("first_name")))
    if kwargs.get("last_name") is not None:
        actions.append(CustomerProfileModel.last_name.set(kwargs.get("last_name")))
    if kwargs.get("data") is not None:
        actions.append(CustomerProfileModel.data.set(kwargs.get("data")))
    customer_profile.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "place_uuid",
        "range_key": "customer_uuid",
    },
    model_funct=get_customer_profile,
)
def delete_customer_profile_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> bool:
    kwargs.get("entity").delete()
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_customer_profile_additional_data(
    company_id: str, customer_uuid: str
) -> CustomerProfileAditionalDataModel:
    return CustomerProfileAditionalDataModel.get(company_id, customer_uuid)


def get_customer_profile_additional_data_count(
    company_id: str, customer_uuid: str
) -> int:
    return CustomerProfileAditionalDataModel.count(
        company_id, CustomerProfileAditionalDataModel.customer_uuid == customer_uuid
    )


def get_customer_profile_additional_data_type(
    info: ResolveInfo,
    customer_profile_additional_data: CustomerProfileAditionalDataModel,
) -> CustomerProfileAdditionalDataType:
    try:
        customer_profile = _get_customer_profile(
            customer_profile_additional_data.place_uuid,
            customer_profile_additional_data.customer_uuid,
        )
        corporation_profile = _get_corporation_profile(
            customer_profile_additional_data.corporation_type,
            customer_profile_additional_data.corporation_uuid,
        )
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    customer_profile_additional_data = customer_profile_additional_data.__dict__[
        "attribute_values"
    ]
    customer_profile_additional_data["customer_profile"] = customer_profile
    customer_profile_additional_data.pop("place_uuid")
    customer_profile_additional_data.pop("customer_uuid")
    customer_profile_additional_data["corporation_profile"] = corporation_profile
    customer_profile_additional_data.pop("corporation_type")
    customer_profile_additional_data.pop("corporation_uuid")
    return CustomerProfileAdditionalDataType(
        **Utility.json_loads(Utility.json_dumps(customer_profile_additional_data))
    )


def resolve_customer_profile_additional_data_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CustomerProfileAdditionalDataType:
    return get_customer_profile_additional_data_type(
        info,
        get_customer_profile_additional_data(
            kwargs.get("company_id"), kwargs.get("customer_uuid")
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["company_id", "customer_uuid", "email"],
    list_type_class=CustomerProfileAdditionalDataListType,
    type_funct=get_customer_profile_additional_data_type,
)
def resolve_customer_profile_additional_data_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    company_id = kwargs.get("company_id")
    email = kwargs.get("email")
    corporation_types = kwargs.get("corporation_types")

    args = []
    inquiry_funct = CustomerProfileAditionalDataModel.scan
    count_funct = CustomerProfileAditionalDataModel.count
    if company_id:
        args = [company_id, None]
        inquiry_funct = CustomerProfileAditionalDataModel.query
        if email:
            inquiry_funct = CustomerProfileAditionalDataModel.email_index.query
            args[1] = CustomerProfileAditionalDataModel.email == email
            count_funct = CustomerProfileAditionalDataModel.email_index.count

    the_filters = None  # We can add filters for the query.
    if corporation_types:
        the_filters &= CustomerProfileAditionalDataModel.corporation_type.is_in(
            *corporation_types
        )
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "company_id",
        "range_key": "customer_uuid",
    },
    range_key_required=True,
    model_funct=get_customer_profile_additional_data,
    count_funct=get_customer_profile_additional_data_count,
    type_funct=get_customer_profile_additional_data_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_customer_profile_additional_data_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    company_id = kwargs.get("company_id")
    customer_uuid = kwargs.get("customer_uuid")
    if kwargs.get("entity") is None:
        CustomerProfileAditionalDataModel(
            company_id,
            customer_uuid,
            **{
                "email": kwargs["email"],
                "place_uuid": kwargs["place_uuid"],
                "corporation_type": kwargs["corporation_type"],
                "corporation_uuid": kwargs["corporation_uuid"],
                "additional_data": kwargs["additional_data"],
                "updated_by": kwargs["updated_by"],
                "created_at": pendulum.now("UTC"),
                "updated_at": pendulum.now("UTC"),
            },
        ).save()
        return

    customer_profile_additional_data = kwargs.get("entity")
    actions = [
        CustomerProfileAditionalDataModel.updated_by.set(kwargs.get("updated_by")),
        CustomerProfileAditionalDataModel.updated_at.set(pendulum.now("UTC")),
    ]
    if kwargs.get("email") is not None:
        actions.append(CustomerProfileAditionalDataModel.email.set(kwargs.get("email")))
    if kwargs.get("corporation_type") is not None:
        actions.append(
            CustomerProfileAditionalDataModel.corporation_type.set(
                kwargs.get("corporation_type")
            )
        )
    if kwargs.get("corporation_uuid") is not None:
        actions.append(
            CustomerProfileAditionalDataModel.corporation_uuid.set(
                kwargs.get("corporation_uuid")
            )
        )
    if kwargs.get("additional_data") is not None:
        actions.append(
            CustomerProfileAditionalDataModel.additional_data.set(
                kwargs.get("additional_data")
            )
        )
    customer_profile_additional_data.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "company_id",
        "range_key": "customer_uuid",
    },
    model_funct=get_customer_profile_additional_data,
)
def delete_customer_profile_additional_data_handler(
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
) -> CorporationProfileModel:
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
        CorporationProfileModel(
            corporation_type,
            corporation_uuid,
            **{
                "external_id": kwargs["external_id"],
                "business_name": kwargs["business_name"],
                "categories": kwargs["categories"],
                "address": kwargs["address"],
                "data": kwargs["data"],
                "updated_by": kwargs["updated_by"],
                "created_at": pendulum.now("UTC"),
                "updated_at": pendulum.now("UTC"),
            },
        ).save()
        return

    corporation_profile = kwargs.get("entity")
    actions = [
        CorporationProfileModel.updated_by.set(kwargs.get("updated_by")),
        CorporationProfileModel.updated_at.set(pendulum.now("UTC")),
    ]
    if kwargs.get("business_name") is not None:
        actions.append(
            CorporationProfileModel.business_name.set(kwargs.get("business_name"))
        )
    if kwargs.get("categories") is not None:
        actions.append(CorporationProfileModel.categories.set(kwargs.get("categories")))
    if kwargs.get("address") is not None:
        actions.append(CorporationProfileModel.address.set(kwargs.get("address")))
    if kwargs.get("data") is not None:
        actions.append(CorporationProfileModel.data.set(kwargs.get("data")))
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
def get_corporation_profile_additional_data(
    company_id: str, corporation_uuid: str
) -> CorporationProfileAdditionalDataModel:
    return CorporationProfileAdditionalDataModel.get(company_id, corporation_uuid)


def get_corporation_profile_additional_data_count(
    company_id: str, corporation_uuid: str
) -> int:
    return CorporationProfileAdditionalDataModel.count(
        company_id,
        CorporationProfileAdditionalDataModel.corporation_uuid == corporation_uuid,
    )


def get_corporation_profile_additional_data_type(
    info: ResolveInfo,
    corporation_profile_additional_data: CorporationProfileAdditionalDataModel,
) -> CorporationProfileAdditionalDataType:
    try:
        corporation_profile = _get_corporation_profile(
            corporation_profile_additional_data.corporation_type,
            corporation_profile_additional_data.corporation_uuid,
        )
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    corporation_profile_additional_data = corporation_profile_additional_data.__dict__[
        "attribute_values"
    ]
    corporation_profile_additional_data["corporation_profile"] = corporation_profile
    corporation_profile_additional_data.pop("corporation_type")
    corporation_profile_additional_data.pop("corporation_uuid")
    return CorporationProfileAdditionalDataType(
        **Utility.json_loads(Utility.json_dumps(corporation_profile_additional_data))
    )


def resolve_corporation_profile_additional_data_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CorporationProfileAdditionalDataType:
    return get_corporation_profile_additional_data_type(
        info,
        get_corporation_profile_additional_data(
            kwargs.get("company_id"), kwargs.get("corporation_uuid")
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["company_id", "corporation_uuid", "external_id"],
    list_type_class=CorporationProfileAdditionalDataListType,
    type_funct=get_corporation_profile_additional_data_type,
)
def resolve_corporation_profile_additional_data_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    company_id = kwargs.get("company_id")
    external_id = kwargs.get("external_id")
    corporation_types = kwargs.get("corporation_types")

    args = []
    inquiry_funct = CorporationProfileAdditionalDataModel.scan
    count_funct = CorporationProfileAdditionalDataModel.count
    if company_id:
        args = [company_id, None]
        inquiry_funct = CorporationProfileAdditionalDataModel.query
        if external_id:
            inquiry_funct = (
                CorporationProfileAdditionalDataModel.external_id_index.query
            )
            args[1] = CorporationProfileAdditionalDataModel.external_id == external_id
            count_funct = CorporationProfileAdditionalDataModel.external_id_index.count

    the_filters = None  # We can add filters for the query.
    if corporation_types:
        the_filters &= CorporationProfileAdditionalDataModel.corporation_type.is_in(
            *corporation_types
        )
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "company_id",
        "range_key": "corporation_uuid",
    },
    range_key_required=True,
    model_funct=get_corporation_profile_additional_data,
    count_funct=get_corporation_profile_additional_data_count,
    type_funct=get_corporation_profile_additional_data_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_update_corporation_profile_additional_data_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    company_id = kwargs.get("company_id")
    corporation_uuid = kwargs.get("corporation_uuid")
    if kwargs.get("entity") is None:
        CorporationProfileAdditionalDataModel(
            company_id,
            corporation_uuid,
            **{
                "external_id": kwargs["external_id"],
                "corporation_type": kwargs["corporation_type"],
                "additional_data": kwargs["additional_data"],
                "updated_by": kwargs["updated_by"],
                "created_at": pendulum.now("UTC"),
                "updated_at": pendulum.now("UTC"),
            },
        ).save()
        return

    corporation_profile_additional_data = kwargs.get("entity")
    actions = [
        CorporationProfileAdditionalDataModel.updated_by.set(kwargs.get("updated_by")),
        CorporationProfileAdditionalDataModel.updated_at.set(pendulum.now("UTC")),
    ]
    if kwargs.get("corporation_type"):
        actions.append(
            CorporationProfileAdditionalDataModel.corporation_type.set(
                kwargs.get("corporation_type")
            )
        )
    if kwargs.get("additional_data"):
        actions.append(
            CorporationProfileAdditionalDataModel.additional_data.set(
                kwargs.get("additional_data")
            )
        )
    corporation_profile_additional_data.update(actions=actions)
    return


@delete_decorator(
    keys={
        "hash_key": "company_id",
        "range_key": "corporation_uuid",
    },
    model_funct=get_corporation_profile_additional_data,
)
def delete_corporation_profile_additional_data_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> bool:
    kwargs.get("entity").delete()
    return True


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def get_customer_chatbot_history(
    company_id: str, timestamp: str
) -> CustomerChatbotHistoryModel:
    return CustomerChatbotHistoryModel.get(company_id, timestamp)


def get_customer_chatbot_history_count(company_id: str, timestamp: str) -> int:
    return CustomerChatbotHistoryModel.count(
        company_id,
        CustomerChatbotHistoryModel.timestamp == timestamp,
    )


def get_customer_chatbot_history_type(
    info: ResolveInfo, customer_chatbot_history: CustomerChatbotHistoryModel
) -> CustomerChatbotHistoryType:
    customer_chatbot_history = customer_chatbot_history.__dict__["attribute_values"]
    return CustomerChatbotHistoryType(
        **Utility.json_loads(Utility.json_dumps(customer_chatbot_history))
    )


def resolve_customer_chatbot_history_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CustomerChatbotHistoryType:
    return get_customer_chatbot_history_type(
        info,
        get_customer_chatbot_history(kwargs.get("company_id"), kwargs.get("timestamp")),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["company_id", "timestamp", "customer_uuid"],
    list_type_class=CustomerChatbotHistoryListType,
    type_funct=get_customer_chatbot_history_type,
)
def resolve_customer_chatbot_history_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    company_id = kwargs.get("company_id")
    customer_uuid = kwargs.get("customer_uuid")
    place_uuids = kwargs.get("place_uuids")
    regions = kwargs.get("regions")
    assistant_types = kwargs.get("assistant_types")

    args = []
    inquiry_funct = CustomerChatbotHistoryModel.scan
    count_funct = CustomerChatbotHistoryModel.count
    if company_id:
        args = [company_id, None]
        inquiry_funct = CustomerChatbotHistoryModel.query
        if customer_uuid:
            inquiry_funct = CustomerChatbotHistoryModel.customer_uuid_index.query
            args[1] = CustomerChatbotHistoryModel.customer_uuid == customer_uuid
            count_funct = CustomerChatbotHistoryModel.customer_uuid_index.count

    the_filters = None  # We can add filters for the query.
    if place_uuids:
        the_filters &= CustomerChatbotHistoryModel.place_uuid.is_in(*place_uuids)
    if regions:
        the_filters &= CustomerChatbotHistoryModel.region.is_in(*regions)
    if assistant_types:
        the_filters &= CustomerChatbotHistoryModel.assistant_type.is_in(
            *assistant_types
        )
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "company_id",
        "range_key": "timestamp",
    },
    range_key_required=True,
    model_funct=get_customer_chatbot_history,
    count_funct=get_customer_chatbot_history_count,
    type_funct=get_customer_chatbot_history_type,
    # data_attributes_except_for_data_diff=data_attributes_except_for_data_diff,
    # activity_history_funct=None,
)
def insert_customer_chatbot_history_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> None:
    company_id = kwargs.get("company_id")
    timestamp = kwargs.get("timestamp")
    if kwargs.get("entity") is None:
        CustomerChatbotHistoryModel(
            company_id,
            timestamp,
            **{
                "customer_uuid": kwargs["customer_uuid"],
                "place_uuid": kwargs["place_uuid"],
                "region": kwargs["region"],
                "assistant_id": kwargs["assistant_id"],
                "thread_id": kwargs["thread_id"],
                "assistant_type": kwargs["assistant_type"],
            },
        ).save()
        return

    return


@delete_decorator(
    keys={
        "hash_key": "company_id",
        "range_key": "timestamp",
    },
    model_funct=get_customer_chatbot_history,
)
def delete_customer_chatbot_history_handler(
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
    company_id: str, collection_uuid: str
) -> UtmTagDataCollectionModel:
    return UtmTagDataCollectionModel.get(company_id, collection_uuid)


def get_utm_tag_data_collection_count(company_id: str, collection_uuid: str) -> int:
    return UtmTagDataCollectionModel.count(
        company_id,
        UtmTagDataCollectionModel.collection_uuid == collection_uuid,
    )


def get_utm_tag_data_collection_type(
    info: ResolveInfo, utm_tag_data_collection: UtmTagDataCollectionModel
) -> UtmTagDataCollectionType:
    try:
        place = _get_place(
            utm_tag_data_collection.region, utm_tag_data_collection.place_uuid
        )

        customer_profile = None
        results = CustomerProfileModel.query(
            place["place_uuid"],
            CustomerProfileModel.customer_uuid == utm_tag_data_collection.customer_uuid,
        )
        results = [result for result in results]
        if len(results) > 0:
            customer_place = results[0]
            customer_profile = _get_customer_profile(
                customer_place.place_uuid, utm_tag_data_collection.customer_uuid
            )
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise e
    utm_tag_data_collection = utm_tag_data_collection.__dict__["attribute_values"]
    utm_tag_data_collection["place"] = place
    utm_tag_data_collection.pop("region")
    utm_tag_data_collection.pop("place_uuid")
    utm_tag_data_collection["customer_profile"] = customer_profile
    utm_tag_data_collection.pop("customer_uuid")
    return UtmTagDataCollectionType(
        **Utility.json_loads(Utility.json_dumps(utm_tag_data_collection))
    )


def resolve_utm_tag_data_collection_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> UtmTagDataCollectionType:
    return get_utm_tag_data_collection_type(
        info,
        get_utm_tag_data_collection(
            kwargs.get("company_id"), kwargs.get("collection_uuid")
        ),
    )


@monitor_decorator
@resolve_list_decorator(
    attributes_to_get=["company_id", "collection_uuid", "tag_name"],
    list_type_class=UtmTagDataCollectionListType,
    type_funct=get_utm_tag_data_collection_type,
)
def resolve_utm_tag_data_collection_list_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> Any:
    company_id = kwargs.get("company_id")
    tag_name = kwargs.get("tag_name")
    place_uuids = kwargs.get("place_uuids")
    customer_uuids = kwargs.get("customer_uuids")
    regions = kwargs.get("regions")
    keyword = kwargs.get("keyword")

    args = []
    inquiry_funct = UtmTagDataCollectionModel.scan
    count_funct = UtmTagDataCollectionModel.count
    if company_id:
        args = [company_id, None]
        inquiry_funct = UtmTagDataCollectionModel.query
        if tag_name:
            inquiry_funct = UtmTagDataCollectionModel.tag_name_index.query
            args[1] = UtmTagDataCollectionModel.tag_name == tag_name
            count_funct = UtmTagDataCollectionModel.tag_name_index.count

    the_filters = None  # We can add filters for the query.
    if place_uuids:
        the_filters &= UtmTagDataCollectionModel.place_uuid.is_in(*place_uuids)
    if customer_uuids:
        the_filters &= UtmTagDataCollectionModel.customer_uuid.is_in(*customer_uuids)
    if regions:
        the_filters &= UtmTagDataCollectionModel.region.is_in(*regions)
    if keyword:
        the_filters &= UtmTagDataCollectionModel.keyword.contains(keyword)
    if the_filters is not None:
        args.append(the_filters)

    return inquiry_funct, count_funct, args


@insert_update_decorator(
    keys={
        "hash_key": "company_id",
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
    company_id = kwargs.get("company_id")
    collection_uuid = kwargs.get("collection_uuid")
    if kwargs.get("entity") is None:
        UtmTagDataCollectionModel(
            company_id,
            collection_uuid,
            **{
                "tag_name": kwargs["tag_name"],
                "place_uuid": kwargs["place_uuid"],
                "customer_uuid": kwargs["customer_uuid"],
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
        "hash_key": "company_id",
        "range_key": "collection_uuid",
    },
    model_funct=get_utm_tag_data_collection,
)
def delete_utm_tag_data_collection_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> bool:
    kwargs.get("entity").delete()
    return True
