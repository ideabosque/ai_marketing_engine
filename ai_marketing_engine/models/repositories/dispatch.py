# -*- coding: utf-8 -*-
"""Backend dispatch boundary for repository and DataLoader selection.

``get_repo(entity_type)`` returns the active repository based on
``Config.DB_BACKEND``. ``get_loaders(context)`` returns the active backend's
request-scoped DataLoader container (DynamoDB ``RequestLoaders`` or PostgreSQL
``PGRequestLoaders``), both exposing the same loader attributes so the nested
type resolvers work unchanged across backends.
"""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from ...handlers.config import Config
from .base import EntityRepository

# --- Repository registry -----------------------------------------------------

_repo_registry: Dict[str, Dict[str, EntityRepository]] = {
    "dynamodb": {},
    "postgresql": {},
}

_dynamodb_repos_initialized = False
_postgresql_repos_initialized = False


def register_repo(backend: str, entity_type: str, repo: EntityRepository) -> None:
    """Register a repository instance for a backend + entity_type."""
    if backend not in _repo_registry:
        raise ValueError(f"Unknown backend: {backend}")
    _repo_registry[backend][entity_type] = repo


def get_repo(entity_type: str) -> EntityRepository:
    """Return the active repository for the given entity type."""
    backend = Config.DB_BACKEND
    repo = _repo_registry.get(backend, {}).get(entity_type)
    if repo is None:
        if backend == "dynamodb":
            _init_dynamodb_repos()
            repo = _repo_registry["dynamodb"].get(entity_type)
        elif backend == "postgresql":
            _init_postgresql_repos()
            repo = _repo_registry["postgresql"].get(entity_type)

    if repo is None:
        registered = list(_repo_registry.get(backend, {}).keys())
        raise KeyError(
            f"No repository registered for entity '{entity_type}' "
            f"on backend '{backend}'. Registered entities: {registered}"
        )
    return repo


def _init_dynamodb_repos() -> None:
    global _dynamodb_repos_initialized
    if _dynamodb_repos_initialized:
        return
    from .dynamodb import register_all as register_dynamodb

    register_dynamodb(_repo_registry["dynamodb"])
    _dynamodb_repos_initialized = True


def _init_postgresql_repos() -> None:
    global _postgresql_repos_initialized
    if _postgresql_repos_initialized:
        return
    from .postgresql import register_all as register_postgresql

    register_postgresql(_repo_registry["postgresql"])
    _postgresql_repos_initialized = True


def clear_registry() -> None:
    """Clear all registered repositories (useful for tests)."""
    global _dynamodb_repos_initialized, _postgresql_repos_initialized
    _repo_registry["dynamodb"].clear()
    _repo_registry["postgresql"].clear()
    _dynamodb_repos_initialized = False
    _postgresql_repos_initialized = False


# --- Request-scoped DataLoader dispatch --------------------------------------


def get_loaders(context: Dict[str, Any]) -> Any:
    """Return request-scoped DataLoaders for the active backend.

    Returns the DynamoDB ``RequestLoaders`` or the PostgreSQL
    ``PGRequestLoaders`` depending on ``Config.DB_BACKEND``. Both containers
    expose the same loader attributes so the nested type resolvers in
    ``types/*`` work unchanged across both backends.
    """
    if context is None:
        context = {}
    loaders = context.get("_batch_loaders")
    if loaders is None:
        if Config.DB_BACKEND == "postgresql":
            from ..postgresql.batch_loaders import PGRequestLoaders as loader_class
        else:
            from ..dynamodb.batch_loaders import RequestLoaders as loader_class
        loaders = loader_class(context)
        context["_batch_loaders"] = loaders
    return loaders


def clear_loaders(context: Dict[str, Any]) -> None:
    """Clear request-scoped DataLoaders from a GraphQL context."""
    if context is not None:
        context.pop("_batch_loaders", None)


__all__ = [
    "get_repo",
    "register_repo",
    "clear_registry",
    "get_loaders",
    "clear_loaders",
]
