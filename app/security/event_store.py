# Centralized security event store used for audit logging, security analytics, incident investigation, and Grafana reporting.

import json
from datetime import datetime, timezone

from app.cache.redis_client import redis_client

import uuid

from app.telemetry.metrics import (
    security_events_total,
    policy_violations_total,
    output_security_violations_total,
    authorization_denied_total,
    rate_limit_violations_total
)

SECURITY_EVENTS_KEY = "security_events"

MAX_STORED_EVENTS = 1000

# Persist security-relevant events to Redis and update Prometheus telemetry used by dashboards and analytics APIs.
def store_security_event(
    event_type: str,
    user: str,
    details: dict
):
    # Generate a normalized event structure to ensure consistent storage and downstream analytics processing.
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "user": user,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "details": details
    }

    # Store newest events first and retain a bounded history to prevent unbounded growth of Redis memory usage.
    redis_client.lpush(
        SECURITY_EVENTS_KEY,
        json.dumps(event)
    )

    redis_client.ltrim(
        SECURITY_EVENTS_KEY,
        0,
        MAX_STORED_EVENTS - 1
    )

    security_events_total.inc()

    if event_type == "policy_violation":
        policy_violations_total.inc()

    elif event_type == "output_security_violation":
        output_security_violations_total.inc()

    elif event_type == "authorization_denied":
        authorization_denied_total.inc()

    elif event_type == "rate_limit_violation":
        rate_limit_violations_total.inc()    

# Retrieve recent security events for administrative investigation and audit workflows.
def get_security_events(limit: int = 20):

    events = redis_client.lrange(
        SECURITY_EVENTS_KEY,
        0,
        limit - 1
    )

    return [
        json.loads(event)
        for event in events
    ]

# Generate aggregated security statistics consumed by administrative APIs and dashboard visualizations.
def get_security_summary():

    events = get_security_events(
        limit=MAX_STORED_EVENTS
    )

    summary = {
        "total_events": len(events),
        "policy_violations": 0,
        "output_security_violations": 0,
        "rate_limit_violations": 0,
        "authorization_denied": 0
    }

    # Aggregate event counts by category to provide high-level security visibility.
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