import json
import os
import time
import traceback
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import requests


RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
TOKEN = uuid4().hex[:10]
REPORT = Path("docs/test_results") / f"live_gateway_integration_results_{RUN_ID}.md"
PRIMARY = {"endpoint_id": "gpt", "part_id": "neprodai", "partition_key": "gpt#neprodai"}
ISOLATION = {
    "endpoint_id": "gpt",
    "part_id": "isolationtest",
    "partition_key": "gpt#isolationtest",
}
GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:8765").rstrip("/")
GRAPHQL_ROUTE = "/{endpoint_id}/ai_marketing_graphql"
AUTH_TOKEN = os.getenv("GATEWAY_AUTH_TOKEN") or os.getenv("ADMIN_STATIC_TOKEN") or ""
REQUEST_TIMEOUT = float(os.getenv("GATEWAY_REQUEST_TIMEOUT", "60"))
SAFE_SETTINGS = {
    "gateway_base_url": GATEWAY_BASE_URL,
    "graphql_route": GRAPHQL_ROUTE,
    "db_backend": "postgresql",
    "db_host": "localhost",
    "db_port": "5432",
    "db_user": "silvaengine",
    "db_password": "<redacted>",
    "db_schema": "silvaengine",
    "pg_table_prefix": "ame_",
    "endpoint_id": PRIMARY["endpoint_id"],
    "part_id": PRIMARY["part_id"],
}

records = []
ids = {}


def parse(raw):
    if isinstance(raw, dict) and "body" in raw:
        try:
            body = json.loads(raw.get("body") or "{}")
        except Exception:
            body = {"rawBody": raw.get("body")}
        return {"http": {k: v for k, v in raw.items() if k != "body"}, "body": body}
    return {"http": None, "body": raw}


def data(rec):
    body = rec.get("output", {}).get("body", {})
    return body.get("data", {}) if isinstance(body, dict) else {}


def path(obj, *keys):
    cur = obj
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def call(sid, model, op, kind, doc, variables=None, tenant=None, expect_error=False, skip_reason=None):
    variables = variables or {}
    tenant = tenant or PRIMARY
    endpoint_id = tenant.get("endpoint_id") or PRIMARY["endpoint_id"]
    part_id = tenant.get("part_id")
    url = f"{GATEWAY_BASE_URL}{GRAPHQL_ROUTE.format(endpoint_id=endpoint_id)}"
    headers = {"Content-Type": "application/json"}
    if part_id:
        headers["Part-Id"] = part_id
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    payload = {"query": doc, "variables": variables}
    args = {
        "method": "POST",
        "url": url,
        "headers": {**headers, "Authorization": "Bearer <redacted>"} if "Authorization" in headers else headers,
        "body": payload,
        "context": {
            "endpoint_id": endpoint_id,
            "part_id": part_id,
            "partition_key": tenant.get("partition_key"),
        },
        "settings": SAFE_SETTINGS,
    }
    if skip_reason:
        rec = {
            "sid": sid,
            "model": model,
            "operation": op,
            "kind": kind,
            "status": "skipped",
            "elapsed_ms": 0,
            "arguments": args,
            "output": {"skip_reason": skip_reason},
        }
        records.append(rec)
        return rec

    start = time.perf_counter()
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        try:
            body = resp.json()
        except Exception:
            body = {"rawBody": resp.text}
        output = {
            "http": {
                "statusCode": resp.status_code,
                "headers": {"content-type": resp.headers.get("content-type")},
            },
            "body": body,
        }
        errors = body.get("errors") if isinstance(body, dict) else None
        http_error = resp.status_code >= 400
        status = "pass" if ((expect_error and (errors or http_error)) or (not expect_error and not errors and not http_error)) else "fail"
        rec = {
            "sid": sid,
            "model": model,
            "operation": op,
            "kind": kind,
            "status": status,
            "elapsed_ms": elapsed,
            "arguments": args,
            "output": output,
        }
    except Exception as exc:
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        rec = {
            "sid": sid,
            "model": model,
            "operation": op,
            "kind": kind,
            "status": "pass" if expect_error else "error",
            "elapsed_ms": elapsed,
            "arguments": args,
            "output": {
                "exception_type": type(exc).__name__,
                "exception": str(exc),
                "traceback": traceback.format_exc(limit=8),
            },
        }
    records.append(rec)
    return rec


Q_PING = "query Ping { ping }"
M_CORP = """mutation($corporationUuid:String,$externalId:String,$corporationType:String,$businessName:String,$categories:[String],$address:JSONCamelCase,$data:JSONCamelCase,$updatedBy:String!){insertUpdateCorporationProfile(corporationUuid:$corporationUuid,externalId:$externalId,corporationType:$corporationType,businessName:$businessName,categories:$categories,address:$address,data:$data,updatedBy:$updatedBy){corporationProfile{partitionKey corporationUuid externalId corporationType businessName categories address data updatedBy createdAt updatedAt}}}"""
Q_CORP = "query($corporationUuid:String!){corporationProfile(corporationUuid:$corporationUuid){partitionKey corporationUuid externalId corporationType businessName categories address data updatedBy}}"
Q_CORP_LIST = "query($externalId:String,$limit:Int,$pageNumber:Int){corporationProfileList(externalId:$externalId,limit:$limit,pageNumber:$pageNumber){pageSize pageNumber total corporationProfileList{partitionKey corporationUuid externalId businessName data}}}"
M_PLACE = """mutation($placeUuid:String,$region:String,$latitude:String,$longitude:String,$businessName:String,$address:String,$phoneNumber:String,$website:String,$types:[String],$corporationUuid:String,$updatedBy:String!){insertUpdatePlace(placeUuid:$placeUuid,region:$region,latitude:$latitude,longitude:$longitude,businessName:$businessName,address:$address,phoneNumber:$phoneNumber,website:$website,types:$types,corporationUuid:$corporationUuid,updatedBy:$updatedBy){place{partitionKey placeUuid region latitude longitude businessName address phoneNumber website types corporationUuid corporationProfile{corporationUuid businessName data} updatedBy createdAt updatedAt}}}"""
Q_PLACE = "query($placeUuid:String!){place(placeUuid:$placeUuid){partitionKey placeUuid region businessName corporationUuid corporationProfile{corporationUuid businessName data}}}"
Q_PLACE_LIST = "query($corporationUuid:String,$region:String,$limit:Int,$pageNumber:Int){placeList(corporationUuid:$corporationUuid,region:$region,limit:$limit,pageNumber:$pageNumber){pageSize pageNumber total placeList{partitionKey placeUuid region businessName corporationUuid}}}"
M_CONTACT = """mutation($contactUuid:String,$placeUuid:String,$email:String,$firstName:String,$lastName:String,$data:JSONCamelCase,$updatedBy:String!){insertUpdateContactProfile(contactUuid:$contactUuid,placeUuid:$placeUuid,email:$email,firstName:$firstName,lastName:$lastName,data:$data,updatedBy:$updatedBy){contactProfile{partitionKey contactUuid email firstName lastName placeUuid place{placeUuid businessName corporationProfile{corporationUuid businessName data}} data updatedBy createdAt updatedAt}}}"""
Q_CONTACT = "query($contactUuid:String,$email:String){contactProfile(contactUuid:$contactUuid,email:$email){partitionKey contactUuid email firstName lastName placeUuid place{placeUuid businessName} data}}"
Q_CONTACT_LIST = "query($placeUuid:String,$email:String,$limit:Int,$pageNumber:Int){contactProfileList(placeUuid:$placeUuid,email:$email,limit:$limit,pageNumber:$pageNumber){pageSize pageNumber total contactProfileList{partitionKey contactUuid email firstName lastName placeUuid data}}}"
M_REQ = """mutation($requestUuid:String,$contactUuid:String,$placeUuid:String,$requestTitle:String,$requestDetail:String,$sourceEmail:String,$notificationEmails:[String],$updatedBy:String!){insertUpdateContactRequest(requestUuid:$requestUuid,contactUuid:$contactUuid,placeUuid:$placeUuid,requestTitle:$requestTitle,requestDetail:$requestDetail,sourceEmail:$sourceEmail,notificationEmails:$notificationEmails,updatedBy:$updatedBy){contactRequest{partitionKey requestUuid contactUuid placeUuid requestTitle requestDetail contactProfile{contactUuid email place{placeUuid businessName corporationProfile{corporationUuid businessName data}} data} updatedBy createdAt updatedAt}}}"""
Q_REQ = "query($contactUuid:String!,$requestUuid:String!){contactRequest(contactUuid:$contactUuid,requestUuid:$requestUuid){partitionKey requestUuid contactUuid placeUuid requestTitle requestDetail contactProfile{contactUuid email}}}"
Q_REQ_LIST = "query($contactUuid:String,$placeUuid:String,$limit:Int,$pageNumber:Int){contactRequestList(contactUuid:$contactUuid,placeUuid:$placeUuid,limit:$limit,pageNumber:$pageNumber){pageSize pageNumber total contactRequestList{partitionKey requestUuid contactUuid placeUuid requestTitle}}}"
M_ATTR = """mutation($dataTypeAttributeName:String!,$valueVersionUuid:String,$dataIdentity:String!,$value:String,$status:String,$updatedBy:String!){insertUpdateAttributeValue(dataTypeAttributeName:$dataTypeAttributeName,valueVersionUuid:$valueVersionUuid,dataIdentity:$dataIdentity,value:$value,status:$status,updatedBy:$updatedBy){attributeValue{partitionKey dataTypeAttributeName valueVersionUuid dataIdentity value status updatedBy createdAt updatedAt}}}"""
Q_ATTR = "query($dataTypeAttributeName:String!,$valueVersionUuid:String!){attributeValue(dataTypeAttributeName:$dataTypeAttributeName,valueVersionUuid:$valueVersionUuid){partitionKey dataTypeAttributeName valueVersionUuid dataIdentity value status updatedBy}}"
Q_ATTR_LIST = "query($dataIdentity:String,$dataTypeAttributeName:String,$statuses:[String],$limit:Int,$pageNumber:Int){attributeValueList(dataIdentity:$dataIdentity,dataTypeAttributeName:$dataTypeAttributeName,statuses:$statuses,limit:$limit,pageNumber:$pageNumber){pageSize pageNumber total attributeValueList{partitionKey dataTypeAttributeName valueVersionUuid dataIdentity value status}}}"
M_ACT = """mutation($id:String!,$dataDiff:JSONCamelCase,$log:String,$type:String,$updatedBy:String!){insertActivityHistory(id:$id,dataDiff:$dataDiff,log:$log,type:$type,updatedBy:$updatedBy){activityHistory{id timestamp log dataDiff type updatedBy updatedAt}}}"""
Q_ACT = "query($id:String!,$timestamp:Int!){activityHistory(id:$id,timestamp:$timestamp){id timestamp log dataDiff type updatedBy updatedAt}}"
Q_ACT_LIST = "query($id:String,$activityType:String,$limit:Int,$pageNumber:Int){activityHistoryList(id:$id,activityType:$activityType,limit:$limit,pageNumber:$pageNumber){pageSize pageNumber total activityHistoryList{id timestamp log type updatedBy}}}"
Q_PRESIGN = "query($objectKey:String!){presignedUploadUrl(objectKey:$objectKey){presignedUrl objectKey}}"
M_DEL_REQ = "mutation($requestUuid:String!){deleteContactRequest(requestUuid:$requestUuid){ok}}"
M_DEL_CONTACT = "mutation($contactUuid:String!){deleteContactProfile(contactUuid:$contactUuid){ok}}"
M_DEL_PLACE = "mutation($placeUuid:String!){deletePlace(placeUuid:$placeUuid){ok}}"
M_DEL_CORP = "mutation($corporationUuid:String!){deleteCorporationProfile(corporationUuid:$corporationUuid){ok}}"
M_DEL_ACT = "mutation($id:String!,$timestamp:Int!){deleteActivityHistory(id:$id,timestamp:$timestamp){ok}}"
M_DEL_ATTR = "mutation($dataTypeAttributeName:String!,$valueVersionUuid:String!){deleteAttributeValue(dataTypeAttributeName:$dataTypeAttributeName,valueVersionUuid:$valueVersionUuid){ok}}"


def main():
    by = "codex_live_graphql"
    corp = {
        "externalId": f"codex-corp-{TOKEN}",
        "corporationType": "test_brand",
        "businessName": f"Codex GraphQL Corp {TOKEN}",
        "categories": ["integration", "graphql"],
        "address": {"line1": "100 GraphQL Way", "city": "Testville"},
        "data": {"tier": "gold", "runToken": TOKEN},
        "updatedBy": by,
    }
    call("AME-GQL-000", "readiness", "ping", "query", Q_PING)
    r = call("AME-GQL-001", "corporation_profile", "insertUpdateCorporationProfile", "mutation", M_CORP, corp)
    ids["corp"] = path(data(r), "insertUpdateCorporationProfile", "corporationProfile", "corporationUuid")
    call("AME-GQL-002", "corporation_profile", "corporationProfile", "query", Q_CORP, {"corporationUuid": ids.get("corp")})
    call("AME-GQL-003", "corporation_profile", "corporationProfileList", "query", Q_CORP_LIST, {"externalId": corp["externalId"], "limit": 10, "pageNumber": 1})
    place = {
        "region": "CA",
        "latitude": "37.7749",
        "longitude": "-122.4194",
        "businessName": f"Codex GraphQL Place {TOKEN}",
        "address": "100 GraphQL Way",
        "phoneNumber": "555-0100",
        "website": "https://example.test",
        "types": ["office"],
        "corporationUuid": ids.get("corp"),
        "updatedBy": by,
    }
    r = call("AME-GQL-004", "place", "insertUpdatePlace", "mutation", M_PLACE, place)
    ids["place"] = path(data(r), "insertUpdatePlace", "place", "placeUuid")
    call("AME-GQL-005", "place", "place", "query", Q_PLACE, {"placeUuid": ids.get("place")})
    call("AME-GQL-006", "place", "placeList", "query", Q_PLACE_LIST, {"corporationUuid": ids.get("corp"), "region": "CA", "limit": 10, "pageNumber": 1})
    email = f"codex-{TOKEN}@example.test"
    contact = {
        "placeUuid": ids.get("place"),
        "email": email,
        "firstName": "Codex",
        "lastName": "Tester",
        "data": {"segment": "integration", "runToken": TOKEN},
        "updatedBy": by,
    }
    r = call("AME-GQL-007", "contact_profile", "insertUpdateContactProfile", "mutation", M_CONTACT, contact)
    ids["contact"] = path(data(r), "insertUpdateContactProfile", "contactProfile", "contactUuid")
    call("AME-GQL-008", "contact_profile", "contactProfile", "query", Q_CONTACT, {"contactUuid": ids.get("contact"), "email": None})
    call("AME-GQL-009", "contact_profile", "contactProfileList", "query", Q_CONTACT_LIST, {"placeUuid": ids.get("place"), "email": email, "limit": 10, "pageNumber": 1})
    req = {
        "contactUuid": ids.get("contact"),
        "placeUuid": ids.get("place"),
        "requestTitle": f"Codex Request {TOKEN}",
        "requestDetail": "Live GraphQL integration request",
        "sourceEmail": email,
        "notificationEmails": ["notify@example.test"],
        "updatedBy": by,
    }
    r = call("AME-GQL-010", "contact_request", "insertUpdateContactRequest", "mutation", M_REQ, req)
    ids["request"] = path(data(r), "insertUpdateContactRequest", "contactRequest", "requestUuid")
    call("AME-GQL-011", "contact_request", "contactRequest", "query", Q_REQ, {"contactUuid": ids.get("contact"), "requestUuid": ids.get("request")})
    call("AME-GQL-012", "contact_request", "contactRequestList", "query", Q_REQ_LIST, {"contactUuid": ids.get("contact"), "placeUuid": ids.get("place"), "limit": 10, "pageNumber": 1})
    dtan = f"contact-direct-{TOKEN}"
    r = call("AME-GQL-013", "attribute_value", "insertUpdateAttributeValue", "mutation", M_ATTR, {"dataTypeAttributeName": dtan, "dataIdentity": ids.get("contact"), "value": "direct-value-1", "status": "active", "updatedBy": by})
    ids["dtan"] = dtan
    ids["attr_version"] = path(data(r), "insertUpdateAttributeValue", "attributeValue", "valueVersionUuid")
    call("AME-GQL-014", "attribute_value", "attributeValue", "query", Q_ATTR, {"dataTypeAttributeName": dtan, "valueVersionUuid": ids.get("attr_version")})
    call("AME-GQL-015", "attribute_value", "attributeValueList", "query", Q_ATTR_LIST, {"dataIdentity": ids.get("contact"), "dataTypeAttributeName": None, "statuses": ["active"], "limit": 20, "pageNumber": 1})
    contact_update = {**contact, "contactUuid": ids.get("contact"), "data": {"segment": "integration-updated", "runToken": TOKEN}}
    call("AME-GQL-016", "attribute_value", "parent data update", "mutation", M_CONTACT, contact_update)
    activity_id = f"codex-activity-{TOKEN}"
    r = call("AME-GQL-017", "activity_history", "insertActivityHistory", "mutation", M_ACT, {"id": activity_id, "dataDiff": {"runToken": TOKEN}, "log": "Codex live GraphQL activity", "type": "codex_live", "updatedBy": by})
    ids["activity_id"] = activity_id
    ids["activity_ts"] = path(data(r), "insertActivityHistory", "activityHistory", "timestamp")
    call("AME-GQL-018", "activity_history", "activityHistory", "query", Q_ACT, {"id": activity_id, "timestamp": ids.get("activity_ts")})
    call("AME-GQL-019", "activity_history", "activityHistoryList", "query", Q_ACT_LIST, {"id": activity_id, "activityType": "codex_live", "limit": 10, "pageNumber": 1})
    call("AME-GQL-020", "nested_graph", "contactRequest nested graph", "query", Q_REQ, {"contactUuid": ids.get("contact"), "requestUuid": ids.get("request")})
    iso = {**corp, "externalId": f"codex-iso-corp-{TOKEN}", "businessName": f"Codex Isolation Corp {TOKEN}"}
    r = call("AME-GQL-021A", "tenancy", "insertUpdateCorporationProfile isolation", "mutation", M_CORP, iso, tenant=ISOLATION)
    ids["iso_corp"] = path(data(r), "insertUpdateCorporationProfile", "corporationProfile", "corporationUuid")
    call("AME-GQL-021B", "tenancy", "corporationProfileList primary", "query", Q_CORP_LIST, {"externalId": corp["externalId"], "limit": 10, "pageNumber": 1}, tenant=PRIMARY)
    call("AME-GQL-021C", "tenancy", "corporationProfileList isolation", "query", Q_CORP_LIST, {"externalId": iso["externalId"], "limit": 10, "pageNumber": 1}, tenant=ISOLATION)
    call("AME-GQL-022", "utility", "presignedUploadUrl", "query", Q_PRESIGN, {"objectKey": f"codex/{TOKEN}.txt"}, skip_reason="AWS/S3 dev-safe settings were not provided")
    call("AME-GQL-NEG-001", "place", "place unknown", "query", Q_PLACE, {"placeUuid": f"missing-{TOKEN}"})
    call("AME-GQL-NEG-002", "contact_request", "unknown contact", "mutation", M_REQ, {**req, "contactUuid": f"missing-contact-{TOKEN}"}, expect_error=True)
    call("AME-GQL-NEG-003", "contact_profile", "duplicate email", "mutation", M_CONTACT, contact, expect_error=True)
    call("AME-GQL-NEG-004", "readiness", "missing tenant", "query", Q_PING, tenant={"endpoint_id": None, "part_id": None, "partition_key": None}, expect_error=True)
    cleanup()
    call("AME-GQL-NEG-005", "place", "place after delete", "query", Q_PLACE, {"placeUuid": ids.get("place")})
    write_report()
    print(json.dumps({"report_path": str(REPORT), "summary": summary(), "ids": ids}, indent=2, default=str))


def cleanup():
    if ids.get("request"):
        call("AME-GQL-023", "contact_request", "deleteContactRequest", "mutation", M_DEL_REQ, {"requestUuid": ids["request"]})
    else:
        call("AME-GQL-023", "contact_request", "deleteContactRequest", "mutation", M_DEL_REQ, skip_reason="requestUuid was not generated")
    if ids.get("contact"):
        call("AME-GQL-024", "contact_profile", "deleteContactProfile", "mutation", M_DEL_CONTACT, {"contactUuid": ids["contact"]})
    else:
        call("AME-GQL-024", "contact_profile", "deleteContactProfile", "mutation", M_DEL_CONTACT, skip_reason="contactUuid was not generated")
    if ids.get("place"):
        call("AME-GQL-025", "place", "deletePlace", "mutation", M_DEL_PLACE, {"placeUuid": ids["place"]})
    else:
        call("AME-GQL-025", "place", "deletePlace", "mutation", M_DEL_PLACE, skip_reason="placeUuid was not generated")
    if ids.get("corp"):
        call("AME-GQL-026", "corporation_profile", "deleteCorporationProfile", "mutation", M_DEL_CORP, {"corporationUuid": ids["corp"]})
    else:
        call("AME-GQL-026", "corporation_profile", "deleteCorporationProfile", "mutation", M_DEL_CORP, skip_reason="corporationUuid was not generated")
    if ids.get("activity_id") and ids.get("activity_ts") is not None:
        call("AME-GQL-027", "activity_history", "deleteActivityHistory", "mutation", M_DEL_ACT, {"id": ids["activity_id"], "timestamp": ids["activity_ts"]})
    else:
        call("AME-GQL-027", "activity_history", "deleteActivityHistory", "mutation", M_DEL_ACT, skip_reason="activity id/timestamp was not generated")
    if ids.get("dtan") and ids.get("attr_version"):
        call("AME-GQL-028", "attribute_value", "deleteAttributeValue", "mutation", M_DEL_ATTR, {"dataTypeAttributeName": ids["dtan"], "valueVersionUuid": ids["attr_version"]})
    else:
        call("AME-GQL-028", "attribute_value", "deleteAttributeValue", "mutation", M_DEL_ATTR, skip_reason="direct attribute key was not generated")
    if ids.get("iso_corp"):
        call("AME-GQL-021D", "tenancy", "deleteCorporationProfile isolation", "mutation", M_DEL_CORP, {"corporationUuid": ids["iso_corp"]}, tenant=ISOLATION)


def summary():
    return {name: sum(1 for r in records if r["status"] == name) for name in ["pass", "fail", "error", "skipped", "blocked"]}


def write_report():
    counts = summary()
    final = "Integration Certified" if counts["fail"] == counts["error"] == counts["blocked"] == 0 else "Not Ready"
    lines = [
        "# Live Gateway Integration Results - ai_marketing_engine GraphQL SOP 2.2.0",
        "",
        f"- Generated at: `{datetime.now().isoformat()}`",
        "- Project / module: `ai_marketing_engine`",
        "- Business domain: `ecommerce`",
        "- Environment target: `dev (local)`",
        f"- Gateway / base URL: `{GATEWAY_BASE_URL}`",
        "- Endpoint: `gpt`",
        "- Partition / namespace: `neprodai`",
        "- Interface URL: `POST /{endpoint_id}/ai_marketing_graphql` through `silvaengine_gateway`",
        "- SOP reference: `docs/integration_scenarios_sop.md`, version `2.2.0` (gateway HTTP mode requested by user)",
        "- Dependency / execution order: `ping -> corporation_profile -> place -> contact_profile -> contact_request -> attribute_value -> activity_history -> presigned_upload_url -> deletes/cleanup`",
        f"- Passed: `{counts['pass']}`",
        f"- Failed: `{counts['fail']}`",
        f"- Error responses: `{counts['error']}`",
        f"- Skipped: `{counts['skipped']}`",
        f"- Blocked: `{counts['blocked']}`",
        f"- Total calls: `{len(records)}`",
        f"- **Final certification status:** `{final}`",
        "",
        "## Executive Summary",
        "",
        "This run executed the confirmed GraphQL-only SOP through HTTP calls to `silvaengine_gateway` against local PostgreSQL. The gateway daemon was started with `silvaengine_gateway.tests.run_daemon`, routed requests to `ai_marketing_engine.main:dispatch_graphql`, recorded every live HTTP GraphQL input and output, and attempted reverse-order GraphQL cleanup for generated test data.",
        "",
        "## Function Results",
        "",
    ]
    for idx, rec in enumerate(records, 1):
        lines.extend([
            f"### {idx}. {rec['sid']} / `{rec['operation']}`",
            f"- Method: `{rec['kind']}`",
            f"- Status: `{rec['status']}`",
            f"- Elapsed: `{rec['elapsed_ms']} ms`",
            f"- Scenario ID: `{rec['sid']}`",
            "",
            "Arguments:",
            "",
            "```json",
            json.dumps(rec["arguments"], indent=2, default=str)[:12000],
            "```",
            "",
            "Output:",
            "",
            "```json",
            json.dumps(rec["output"], indent=2, default=str)[:16000],
            "```",
            "",
        ])
    problems = [r for r in records if r["status"] in ("fail", "error", "blocked")]
    lines.extend([
        "## Coverage Analysis",
        "",
        "| Area | Covered | Total | Notes |",
        "|---|---:|---:|---|",
        f"| Required GraphQL calls | {sum(1 for r in records if r['sid'].startswith('AME-GQL') and r['status'] == 'pass')} | {sum(1 for r in records if r['sid'].startswith('AME-GQL'))} | skipped utility is not counted as pass |",
        "",
        "## Defect Analysis",
        "",
        "| ID | Severity | Title | Affected call(s) | Recommendation |",
        "|---|---|---|---|---|",
    ])
    if not problems:
        lines.append("| none | n/a | No blocking defects from executed calls | n/a | n/a |")
    else:
        for num, rec in enumerate(problems, 1):
            title = json.dumps(rec.get("output", {}), default=str).replace("|", "/")[:180]
            lines.append(f"| DEF-{num:03d} | blocking | `{rec['status']}`: {title} | {rec['sid']} | Review Function Results and fix GraphQL/backend behavior. |")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
