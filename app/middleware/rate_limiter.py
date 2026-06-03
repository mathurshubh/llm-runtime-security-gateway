# Simple Redis-backed abuse prevention control for per-user API request throttling

from fastapi import HTTPException

from app.telemetry.logger import logger
from app.cache.redis_client import redis_client
from app.security.event_store import store_security_event

from app.telemetry.metrics import (
    rate_limit_violations_total
)

RATE_LIMIT_WINDOW = 60
MAX_REQUESTS = 5


# Enforce distributed rate limits using Redis-backed counters to provide consistent abuse prevention across gateway instances.
def check_rate_limit(identity: str, user: str):

    redis_key = f"rate_limit:{identity}"

    current_count = redis_client.get(redis_key)

    if current_count is None:

        # Initialize a new counter with a TTL-based enforcement window to avoid manual cleanup of stale rate-limit state.
        redis_client.set(
            redis_key,
            1,
            ex=RATE_LIMIT_WINDOW
        )

        return

    current_count = int(current_count)

    # Requests exceeding the configured threshold are blocked before expensive security processing or LLM inference occurs.
    if current_count >= MAX_REQUESTS:

        rate_limit_violations_total.inc()
        
        logger.warning(
            "\n🚨 RATE LIMIT EXCEEDED 🚨",
            user=user,
            request_count=current_count,
            limit=MAX_REQUESTS,
            window_seconds=RATE_LIMIT_WINDOW
        )

        # Persist rate-limit violations for auditability, security analytics, and abuse investigations.
        store_security_event(
            event_type="rate_limit_violation",
            user=user,
            details={
                "request_count": current_count,
                "limit": MAX_REQUESTS,
                "window_seconds": RATE_LIMIT_WINDOW
            }
        )

        raise HTTPException(
            status_code=429,
            detail={
                "message": "Rate limit exceeded",
                "max_requests": MAX_REQUESTS,
                "window_seconds": RATE_LIMIT_WINDOW
            }
        )

    redis_client.incr(redis_key)