# -*- coding: utf-8 -*-
"""PostgreSQL repositories for the PostgreSQL backend."""
from __future__ import print_function

__author__ = "bibow"

from typing import Dict

from ..base import EntityRepository


def register_all(registry: Dict[str, EntityRepository]) -> None:
    """Register all PostgreSQL repositories into the given registry dict."""
    from .activity_history_repo import ActivityHistoryPGRepository
    from .attribute_value_repo import AttributeValuePGRepository
    from .contact_profile_repo import ContactProfilePGRepository
    from .contact_request_repo import ContactRequestPGRepository
    from .corporation_profile_repo import CorporationProfilePGRepository
    from .place_repo import PlacePGRepository

    repos = [
        PlacePGRepository(),
        CorporationProfilePGRepository(),
        ContactProfilePGRepository(),
        ContactRequestPGRepository(),
        AttributeValuePGRepository(),
        ActivityHistoryPGRepository(),
    ]
    for repo in repos:
        registry[repo.entity_type] = repo


__all__ = ["register_all"]
