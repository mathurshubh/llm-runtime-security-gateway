import json
from datetime import datetime, timezone

from app.cache.redis_client import redis_client

import uuid

from app.telemetry.metrics import (
    security_events_total,
    policy_violations_total,
    output_security_violations_total,
    authorization_denied_total
)


def store_security_event(
    event_type: str,
    user: str,
    details: dict
):

    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "user": user,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "details": details
    }

    redis_client.lpush(
        "security_events",
        json.dumps(event)
    )

    redis_client.ltrim(
        "security_events",
        0,
        999
    )

    security_events_total.inc()

    if event_type == "policy_violation":
        policy_violations_total.inc()

    elif event_type == "output_security_violation":
        output_security_violations_total.inc()

    elif event_type == "authorization_denied":
        authorization_denied_total.inc()


def get_security_events(limit: int = 20):

    events = redis_client.lrange(
        "security_events",
        0,
        limit - 1
    )

    return [
        json.loads(event)
        for event in events
    ]


def get_security_summary():

    events = get_security_events(limit=1000)

    summary = {
        "total_events": len(events),
        "policy_violations": 0,
        "output_security_violations": 0,
        "rate_limit_violations": 0,
        "authorization_denied": 0
    }

    for event in events:

        event_type = event.get("event_type")

        if event_type == "policy_violation":
            summary["policy_violations"] += 1

        elif event_type == "output_security_violation":
            summary["output_security_violations"] += 1

        elif event_type == "rate_limit_violation":
            summary["rate_limit_violations"] += 1

        elif event_type == "authorization_denied":
            summary["authorization_denied"] += 1

    return summary