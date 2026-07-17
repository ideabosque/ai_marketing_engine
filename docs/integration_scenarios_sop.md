# Continuous Integration Scenarios SOP - ai_marketing_engine GraphQL

## 1. Document Control

| Field | Value |
|---|---|
| SOP title | AI Marketing Engine - GraphQL Query and Mutation Integration SOP |
| Version | 2.2.0 |
| Owner / contact | ideabosque@gmail.com |
| Last updated | 2026-07-16 |
| Business domain | ecommerce (CRM / marketing entities) |
| Target environment | dev (local) |
| Approval status | confirmed by user on 2026-07-16 |

## 2. Purpose and Scope

Certify the live GraphQL surface of `ai_marketing_engine` by executing every query
and mutation exposed in `ai_marketing_engine.schema` through HTTP POST calls to
`silvaengine_gateway` route `/{endpoint_id}/ai_marketing_graphql`, which dispatches to
`ai_marketing_engine.main:dispatch_graphql`.

This SOP is about **GraphQL operation coverage only**. Results must be based on live GraphQL inputs and outputs only. Backing-store setup may be required to make GraphQL executable, but SQL or repository checks are not part of certification output.

- **In scope:** every GraphQL query and mutation for `corporation_profile`,
  `place`, `contact_profile`, `contact_request`, `attribute_value`,
  `activity_history`, plus `ping`.
- **Utility query in scope when configured:** `presigned_upload_url`, only when
  local AWS/S3 settings are available and safe for the dev environment.
- **In scope gateway dependency:** `silvaengine_gateway` started by `python -m silvaengine_gateway.tests.run_daemon`; route `POST /{endpoint_id}/ai_marketing_graphql`.
- **Out of scope:** DynamoDB certification, direct repository-only tests, direct SQL-only tests, SQL reconciliation results, schema migration certification, and other engines.
- **System under test:** `silvaengine_gateway` HTTP GraphQL route for `ai_marketing_engine.main:dispatch_graphql`.

## 3. Environment and Access

| Item | Value / source |
|---|---|
| Environment target | dev (local) |
| GraphQL entry point | `POST /{endpoint_id}/ai_marketing_graphql` through `silvaengine_gateway` |
| Backend for this run | PostgreSQL (`db_backend=postgresql`) |
| Data store | PostgreSQL `localhost:5432/silvaengine`, table prefix `ame_` |
| Required settings | gateway `.env`, `GATEWAY_AUTH_PROVIDER`, `ADMIN_STATIC_TOKEN`, `db_backend`, `db_host`, `db_port`, `db_user`, `db_password`, `db_schema`, `AME_PG_TABLE_PREFIX`, `endpoint_id`, `Part-Id` header |
| Tenant model | `partition_key = "{endpoint_id}#{part_id}"` |
| Primary tenant | `gpt#neprodai` |
| Isolation tenant | `gpt#isolationtest` |

Secrets must not be written to reports. Redact `db_password`, AWS keys, tokens,
and other credentials as `<redacted>` in Function Results.

## 4. GraphQL Model Dependencies

Execute GraphQL operations in dependency order. A model's write mutation must
pass before child-model mutations that depend on its generated identifiers.
Independent models may run after GraphQL readiness.

| Order | Model / surface | Depends on | Provides identifiers for |
|---|---|---|---|
| 0 | `ping` | Config initialized | all GraphQL calls |
| 1 | `corporation_profile` | `ping` | `place.corporation_uuid`, corporation attribute data |
| 2 | `place` | `corporation_profile` | `contact_profile.place_uuid`, `contact_request.place_uuid` |
| 3 | `contact_profile` | `place` | `contact_request.contact_uuid`, contact attribute data |
| 4 | `contact_request` | `contact_profile`, `place` | nested graph read path |
| 5 | `attribute_value` | corporation/contact `data` writes, or direct attribute mutation input | attribute query/list validation |
| 6 | `activity_history` | `ping` | audit query/list validation |
| 7 | `presigned_upload_url` | AWS/S3 settings available | utility query validation |
| 8 | deletes / cleanup | created rows from orders 1-6 | clean test state |

## 5. Test Data Requirements

| Asset type | Count | Required fields / dependencies |
|---|---:|---|
| corporation_profile | 2 | one primary tenant, one isolation tenant; include `data` |
| place | 2 | linked to created `corporation_uuid` |
| contact_profile | 2 | linked to created `place_uuid`; unique `email`; include `data` |
| contact_request | 2 | linked to created `contact_uuid` and `place_uuid` |
| attribute_value | 2 | created by parent `data` writes and optionally one direct mutation |
| activity_history | 2 | independent audit rows |

All test rows must use generated, run-unique values and must be deleted in
reverse dependency order during cleanup.

## 6. GraphQL Operation Matrix

Every operation below must be executed as an HTTP GraphQL call through `silvaengine_gateway`; direct in-process `dispatch_graphql` calls are not valid for this SOP version. Each row must
produce a Function Results entry with exact live input and output.

| ID | Model / surface | GraphQL operation | Kind | Depends on | Required validation |
|---|---|---|---|---|---|
| AME-GQL-000 | readiness | `ping` | query | Config initialized | returns non-empty string; no GraphQL errors |
| AME-GQL-001 | corporation_profile | `insertUpdateCorporationProfile` | mutation | AME-GQL-000 | returns `corporationProfile.corporationUuid`; includes requested fields and `data` if selected |
| AME-GQL-002 | corporation_profile | `corporationProfile` | query | AME-GQL-001 | fetch by `corporationUuid` returns created corporation |
| AME-GQL-003 | corporation_profile | `corporationProfileList` | query | AME-GQL-001 | filter returns created corporation; pagination metadata is correct |
| AME-GQL-004 | place | `insertUpdatePlace` | mutation | AME-GQL-001 | returns `place.placeUuid`; stores parent `corporationUuid` |
| AME-GQL-005 | place | `place` | query | AME-GQL-004 | fetch by `placeUuid` returns created place and nested `corporationProfile` |
| AME-GQL-006 | place | `placeList` | query | AME-GQL-004 | filter by `corporationUuid` or region returns created place |
| AME-GQL-007 | contact_profile | `insertUpdateContactProfile` | mutation | AME-GQL-004 | returns `contactProfile.contactUuid`; stores parent `placeUuid`; writes `data` |
| AME-GQL-008 | contact_profile | `contactProfile` | query | AME-GQL-007 | fetch by `contactUuid` or `email` returns created contact, nested `place`, and `data` |
| AME-GQL-009 | contact_profile | `contactProfileList` | query | AME-GQL-007 | filter by `placeUuid` or `email` returns created contact |
| AME-GQL-010 | contact_request | `insertUpdateContactRequest` | mutation | AME-GQL-007, AME-GQL-004 | returns `contactRequest.requestUuid`; keeps `contactUuid` and `placeUuid` |
| AME-GQL-011 | contact_request | `contactRequest` | query | AME-GQL-010 | fetch by `requestUuid` and `contactUuid` returns created request with nested `contactProfile` |
| AME-GQL-012 | contact_request | `contactRequestList` | query | AME-GQL-010 | filter by `contactUuid` or `placeUuid` returns created request |
| AME-GQL-013 | attribute_value | `insertUpdateAttributeValue` | mutation | AME-GQL-001 or AME-GQL-007 | direct attribute mutation returns `attributeValue.valueVersionUuid` |
| AME-GQL-014 | attribute_value | `attributeValue` | query | AME-GQL-013 | fetch by `dataTypeAttributeName` and `valueVersionUuid` returns created attribute |
| AME-GQL-015 | attribute_value | `attributeValueList` | query | AME-GQL-001, AME-GQL-007, or AME-GQL-013 | list by `dataIdentity`, `dataTypeAttributeName`, or `statuses` returns expected active values |
| AME-GQL-016 | attribute_value | parent `data` update through `insertUpdateCorporationProfile` or `insertUpdateContactProfile` | mutation | AME-GQL-001 or AME-GQL-007 | previous value becomes inactive and new active value is visible through GraphQL |
| AME-GQL-017 | activity_history | `insertActivityHistory` | mutation | AME-GQL-000 | returns `activityHistory.id` and `timestamp` |
| AME-GQL-018 | activity_history | `activityHistory` | query | AME-GQL-017 | fetch by `id` and `timestamp` returns created activity |
| AME-GQL-019 | activity_history | `activityHistoryList` | query | AME-GQL-017 | filter by `id` and `activityType` returns created activity |
| AME-GQL-020 | nested graph | `contactRequest` with nested `contactProfile { place { corporationProfile { data } } data }` | query | AME-GQL-001 through AME-GQL-010 | full dependent model graph resolves from GraphQL response |
| AME-GQL-021 | tenancy | create/list operations under primary and isolation tenants | query+mutation | AME-GQL-001 through AME-GQL-012 | each tenant sees only its own GraphQL rows |
| AME-GQL-022 | utility | `presignedUploadUrl` | query | AWS/S3 settings available | returns usable URL fields or is marked skipped when not configured |
| AME-GQL-023 | contact_request | `deleteContactRequest` | mutation | AME-GQL-010 | returns `ok=true`; subsequent query returns null/error per schema behavior |
| AME-GQL-024 | contact_profile | `deleteContactProfile` | mutation | AME-GQL-023 | returns `ok=true`; subsequent query returns null/error per schema behavior |
| AME-GQL-025 | place | `deletePlace` | mutation | AME-GQL-024 | returns `ok=true`; subsequent query returns null/error per schema behavior |
| AME-GQL-026 | corporation_profile | `deleteCorporationProfile` | mutation | AME-GQL-025 | returns `ok=true`; subsequent query returns null/error per schema behavior |
| AME-GQL-027 | activity_history | `deleteActivityHistory` | mutation | AME-GQL-017 | returns `ok=true`; subsequent query returns null/error per schema behavior |
| AME-GQL-028 | attribute_value | `deleteAttributeValue` | mutation | AME-GQL-013 | returns `ok=true`; subsequent query/list no longer returns deleted direct attribute |

## 7. Required GraphQL Input and Output Evidence

For each operation in Section 6, record a Function Results entry in the live
results report.

Each Function Results entry must include:

- Scenario ID, model, operation name, query/mutation kind, and dependency IDs.
- Exact HTTP method, URL, headers with secrets redacted, GraphQL document text, and GraphQL variables.
- Request context: URL `endpoint_id`, `Part-Id` header, derived `partition_key`, and `connection_id` if present.
- Gateway/runtime settings used, with secrets redacted.
- Returned GraphQL `data`.
- Returned GraphQL `errors`, including exception class/message when present.
- Elapsed time, status (`pass`, `fail`, `skipped`, or `blocked`), and generated IDs.

A GraphQL operation cannot pass unless both the live input and live output are
present in `docs/test_results/live_integration_results_<YYYYMMDD_HHMMSS>.md`.

## 8. Negative GraphQL Scenarios

| ID | Operation | Fault | Expected GraphQL behavior |
|---|---|---|---|
| AME-GQL-NEG-001 | `place` | unknown `placeUuid` | data is null or schema-consistent not-found behavior; no crash |
| AME-GQL-NEG-002 | `insertUpdateContactRequest` | unknown `contactUuid` | GraphQL errors include validation failure; no request row returned |
| AME-GQL-NEG-003 | `insertUpdateContactProfile` | duplicate `email` in same tenant | GraphQL errors include uniqueness failure; duplicate row not returned |
| AME-GQL-NEG-004 | any tenant-scoped operation | missing `endpoint_id` or `part_id` | GraphQL call fails cleanly with partition-key error |
| AME-GQL-NEG-005 | child query | parent deleted before child read | schema-consistent null/error behavior; no server crash |

## 9. GraphQL-Only Result Rule

Certification output must include only HTTP GraphQL Function Results from `silvaengine_gateway`. Do not include SQL reconciliation, direct repository checks, raw table counts, or migration verification in the live result report. GraphQL delete mutations and follow-up GraphQL queries through the gateway are the only cleanup evidence used for this SOP.

## 10. Entry and Exit Criteria

**Entry:** SOP confirmed; `silvaengine_gateway` supports `ai_marketing_engine`; `run_daemon.py` can start locally; gateway auth token is available; runtime settings are available; backend initialized; any required backing schema exists for GraphQL operations.

**Exit:** every GraphQL operation in Section 6 is passed or explicitly skipped with a valid reason; every negative scenario in Section 8 is passed or explicitly skipped with a valid reason; all generated test rows are cleaned up through GraphQL delete mutations; every live GraphQL input and output is recorded in the live results report; no blocking GraphQL defects remain.

## 11. CI Trigger and Cadence

| Trigger | Scope | Required to pass |
|---|---|---|
| Manual | all Section 6 GraphQL operations and Section 8 negative scenarios | yes |
| Pre-release | full GraphQL operation matrix for each supported backend | yes |

## 12. Reporting and Certification Expectations

- **Report format:** markdown, written to `docs/test_results/`.
- **Live results report:** every execution run must write
  `docs/test_results/live_integration_results_<YYYYMMDD_HHMMSS>.md`.
- **Function Results are mandatory:** one entry per HTTP GraphQL operation only. SQL or direct database results must not be included in this SOP report.
- **Certification decision:** one of Integration Certified / Ready for UAT /
  Ready for Production / Ready with Conditions / Not Ready.
- **Distribution:** repo owner (ideabosque@gmail.com).

## 13. Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Test owner | (pending) | 2026-07-16 | (pending) |

---

### Known gaps / assumptions

- `presignedUploadUrl` is a utility query, not a CRM model operation. It is skipped
  unless local AWS/S3 settings are configured for dev.
- Live HTTP gateway routing is in scope; GraphQL must be executed through
  `silvaengine_gateway` route `POST /{endpoint_id}/ai_marketing_graphql`.
- SQL reconciliation is intentionally excluded from this SOP. The live result is about GraphQL inputs and GraphQL outputs only.
