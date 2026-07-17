# -*- coding: utf-8 -*-
"""Alembic migration environment for ai_marketing_engine PostgreSQL backend.

URL resolution priority:
    1. ``DATABASE_URL`` environment variable
    2. ``Config`` setting (when already initialized at runtime)
    3. ``sqlalchemy.url`` in ``alembic.ini`` (fallback)

Table-prefix resolution priority:
    1. ``PG_TABLE_PREFIX`` environment variable
    2. ``Config.PG_TABLE_PREFIX``
    3. ``"ame_"``
"""
from __future__ import print_function

__author__ = "bibow"

import importlib
import logging
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# --- Project path setup ------------------------------------------------------
_this_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(os.path.dirname(_this_dir))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

_logger = logging.getLogger(__name__)

# --- URL resolution ----------------------------------------------------------
database_url = os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)
else:
    try:
        from ai_marketing_engine.handlers.config import Config

        setting = Config.get_setting()
        if setting and setting.get("db_host"):
            from urllib.parse import quote_plus

            password = quote_plus(setting["db_password"])
            db_url = (
                f"postgresql+psycopg2://{setting['db_user']}:{password}"
                f"@{setting['db_host']}:{setting['db_port']}/{setting['db_schema']}"
            )
            config.set_main_option("sqlalchemy.url", db_url)
    except Exception:
        _logger.debug("Config not available; falling back to alembic.ini URL.")

# --- Table prefix ------------------------------------------------------------
pg_table_prefix = os.environ.get("PG_TABLE_PREFIX")
if not pg_table_prefix:
    try:
        from ai_marketing_engine.handlers.config import Config

        pg_table_prefix = Config.PG_TABLE_PREFIX
    except Exception:
        pg_table_prefix = "ame_"

from ai_marketing_engine.models.postgresql.base import Base

Base.table_prefix = pg_table_prefix or "ame_"

# --- Import all models so Base.metadata is populated -------------------------
_MODEL_MODULES = [
    "place",
    "corporation_profile",
    "contact_profile",
    "contact_request",
    "attribute_value",
    "activity_history",
]


def _import_all_models() -> None:
    for mod_name in _MODEL_MODULES:
        try:
            importlib.import_module(
                f"ai_marketing_engine.models.postgresql.{mod_name}"
            )
        except ImportError as exc:
            _logger.debug("PostgreSQL model not available: %s (%s)", mod_name, exc)


_import_all_models()

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
