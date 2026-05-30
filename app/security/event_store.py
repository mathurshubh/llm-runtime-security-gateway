import json
from datetime import datetime, timezone

from app.cache.redis_client import redis_client

import uuid


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