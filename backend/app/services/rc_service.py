from __future__ import annotations

from datetime import datetime, timezone

from ringcentral import SDK

from app.core.config import settings


def fetch_analytics(time_from_iso: str, time_to_iso: str) -> list[dict]:
    """Llama la RC Analytics API y devuelve filas listas para insertar en call_analytics.

    Función síncrona pura — sin acceso a DB. Debe llamarse desde asyncio.run_in_executor.
    """
    rcsdk = SDK(
        settings.RC_APP_CLIENT_ID,
        settings.RC_APP_CLIENT_SECRET,
        settings.RC_SERVER_URL,
    )
    platform = rcsdk.platform()
    platform.login(jwt=settings.RC_USER_JWT)

    extension_ids = [e.strip() for e in settings.RC_EXTENSION_IDS.split(",") if e.strip()]

    body_params = {
        "grouping": {
            "groupBy": "Users",
            "keys": extension_ids,
        },
        "timeSettings": {
            "timeZone": "America/New_York",
            "timeRange": {
                "timeFrom": time_from_iso,
                "timeTo":   time_to_iso,
            },
        },
        "callFilters": {
            "directions": ["Inbound", "Outbound"],
            "origins":    ["Internal", "External"],
        },
        "responseOptions": {
            "counters": {
                "allCalls":         {"aggregationType": "Sum"},
                "callsByDirection": {"aggregationType": "Sum"},
                "callsByType":      {"aggregationType": "Sum"},
                "callsByOrigin":    {"aggregationType": "Sum"},
                "callsByResponse":  {"aggregationType": "Sum"},
                "callsByResult":    {"aggregationType": "Sum"},
            },
            "timers": {
                "allCallsDuration": {"aggregationType": "Sum"},
            },
        },
    }

    resp = platform.post(
        "/analytics/calls/v1/accounts/~/aggregation/fetch",
        body_params,
        {"perPage": 100},
    )
    records = resp.json_dict().get("data", {}).get("records", [])

    tf = datetime.fromisoformat(time_from_iso.replace("Z", "+00:00"))
    tt = datetime.fromisoformat(time_to_iso.replace("Z", "+00:00"))

    rows: list[dict] = []
    for record in records:
        info     = record.get("info", {})
        counters = record.get("counters", {})
        timers   = record.get("timers", {})

        ext_num  = info.get("extensionNumber", "-")
        name     = info.get("name", "-")

        total    = int(counters.get("allCalls", {}).get("values", 0))
        by_dir   = counters.get("callsByDirection", {}).get("values", {})
        inbound  = int(by_dir.get("inbound", 0))
        outbound = int(by_dir.get("outbound", 0))

        by_type    = counters.get("callsByType", {}).get("values", {})
        direct     = int(by_type.get("direct", 0))
        from_queue = int(by_type.get("fromQueue", 0))
        transferred = int(by_type.get("transferred", 0))

        by_origin = counters.get("callsByOrigin", {}).get("values", {})
        external  = int(by_origin.get("external", 0))
        internal  = int(by_origin.get("internal", 0))

        by_resp   = counters.get("callsByResponse", {}).get("values", {})
        answered  = int(by_resp.get("answered", 0))
        not_ans   = int(by_resp.get("notAnswered", 0))

        by_result       = counters.get("callsByResult", {}).get("values", {})
        completed       = int(by_result.get("completed", 0))
        abandoned       = int(by_result.get("abandoned", 0))
        voicemail       = int(by_result.get("voicemail", 0))
        answered_else   = int(by_result.get("answeredElsewhere", 0))
        missed          = int(by_result.get("missed", 0))
        unknown         = int(by_result.get("unknown", 0))
        transferred_out = int(by_result.get("transferred", 0))

        exclusion    = max(answered_else, transferred_out)
        portal_equiv = total - exclusion - (unknown if voicemail > 0 else missed)

        secs = int(timers.get("allCalls", {}).get("values", 0))

        rows.append({
            "time_from":        tf,
            "time_to":          tt,
            "extension_number": ext_num,
            "extension_name":   name,
            "total_calls":      total,
            "inbound":          inbound,
            "outbound":         outbound,
            "direct":           direct,
            "from_queue":       from_queue,
            "transferred":      transferred,
            "portal_equiv":     portal_equiv,
            "duration_seconds": secs,
            "external":         external,
            "internal":         internal,
            "answered":         answered,
            "not_answered":     not_ans,
            "completed":        completed,
            "abandoned":        abandoned,
            "voicemail":        voicemail,
        })

    return rows
