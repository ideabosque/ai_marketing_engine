# -*- coding: utf-8 -*-
"""DynamoDB repositories — thin wrappers over existing PynamoDB model funcs."""
from __future__ import print_function

__author__ = "bibow"

from typing import Dict

from ..base import EntityRepository


def register_all(registry: Dict[str, EntityRepository]) -> None:
    """Register all DynamoDB repositories into the given registry dict."""
    from .activity_history_repo import ActivityHistoryRepository
    from .attribute_value_repo import AttributeValueRepository
    from .contact_profile_repo import ContactProfileRepository
    from .contact_request_repo import ContactRequestRepository
    from .corporation_profile_repo import CorporationProfileRepository
    from .place_repo import PlaceRepository

    repos = [
        PlaceRepository(),
        CorporationProfileRepository(),
        ContactProfileRepository(),
        ContactRequestRepository(),
        AttributeValueRepository(),
        ActivityHistoryRepository(),
    ]
    for repo in repos:
        registry[repo.entity_type] = repo


__all__ = ["register_all"]
