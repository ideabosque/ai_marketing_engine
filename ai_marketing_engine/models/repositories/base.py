# -*- coding: utf-8 -*-
"""Repository abstraction boundary for dual-backend persistence.

Each repository returns normalized dictionaries / GraphQL types or explicit
scalar results. PynamoDB or SQLAlchemy instances must not leak above this
boundary.
"""
from __future__ import print_function

__author__ = "bibow"

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class EntityRepository(ABC):
    """Abstract base class for entity repositories."""

    @property
    @abstractmethod
    def entity_type(self) -> str:
        """Return the entity type name (e.g. 'place')."""
        ...

    @abstractmethod
    def get(self, **keys: Any) -> Optional[Dict[str, Any]]:
        """Return one normalized entity dict or None."""
        ...

    @abstractmethod
    def count(self, **keys: Any) -> int:
        """Return matching row count for existence / dependency checks."""
        ...

    @abstractmethod
    def list(self, info: Any, **filters: Any) -> Any:
        """Return the same list/connection shape expected by GraphQL."""
        ...

    @abstractmethod
    def insert_update(self, info: Any, **kwargs: Any) -> Any:
        """Create or update one entity and return the GraphQL type/dict."""
        ...

    @abstractmethod
    def delete(self, info: Any, **kwargs: Any) -> bool:
        """Delete one entity or return False for blocked-delete behavior."""
        ...

    def resolve_single(self, info: Any, **kwargs: Any) -> Any:
        """Resolve a single entity for the top-level query field."""
        raise NotImplementedError

    def get_type(self, info: Any, instance: Any) -> Any:
        """Convert a persistence row/instance into its GraphQL type."""
        raise NotImplementedError


class RepositoryError(Exception):
    """Base exception for repository-level errors."""


class EntityNotFoundError(RepositoryError):
    """Raised when an entity is not found during update/delete."""


class DependencyExistsError(RepositoryError):
    """Raised when a delete is blocked by existing child dependencies."""


__all__ = [
    "EntityRepository",
    "RepositoryError",
    "EntityNotFoundError",
    "DependencyExistsError",
]
