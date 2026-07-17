# ai_marketing_engine — PostgreSQL migrations

Alembic migrations for the PostgreSQL backend (`db_backend=postgresql`). The
DynamoDB backend does not use these — it creates tables via PynamoDB.

## Prerequisites

```bash
pip install "ai-marketing-engine[postgresql]"
```

## Configuration

The database URL and table prefix are resolved by `alembic/env.py` in this
order:

1. `DATABASE_URL` environment variable (e.g.
   `postgresql+psycopg2://user:pass@host:5432/dbname`)
2. An initialized `Config` (uses `db_host`/`db_port`/`db_user`/`db_password`/`db_schema`)
3. `sqlalchemy.url` in `alembic.ini` (placeholder fallback)

Table prefix (default `ame_`):

1. `PG_TABLE_PREFIX` environment variable
2. `Config.PG_TABLE_PREFIX`

## Usage

```bash
cd ai_marketing_engine/migration
export DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/ame"
export PG_TABLE_PREFIX="ame_"

alembic upgrade head      # apply all migrations (0001..0007)
alembic downgrade base    # roll everything back
alembic current           # show current revision
```

## Revisions

| Rev  | Description                                         | RLS |
|------|-----------------------------------------------------|-----|
| 0001 | `places`                                            | yes |
| 0002 | `corporation_profiles`                              | yes |
| 0003 | `contact_profiles`                                  | yes |
| 0004 | `contact_requests`                                  | yes |
| 0005 | `attribute_values` (partition_key column)           | yes |
| 0006 | `activity_history` (global, no partition_key)       | no  |
| 0007 | Enable Row-Level Security tenant-isolation policies | —   |

## Row-Level Security

Migration `0007` enables RLS on every partition-keyed table with a
`tenant_isolation` policy:

```sql
USING (partition_key = current_setting('app.tenant_id', true))
```

Each request sets the tenant via `SET app.tenant_id = '<endpoint_id>#<part_id>'`
(handled by `Config._set_rls_context` / `main.py`). `activity_history` has no
`partition_key` and is intentionally excluded.

Note: `create_all` (used when `initialize_tables=True`) also applies these RLS
policies via `utils.rls.create_rls_policies`, so a fresh deployment is protected
even without running Alembic. Use Alembic for controlled, versioned schema
changes in shared environments.
