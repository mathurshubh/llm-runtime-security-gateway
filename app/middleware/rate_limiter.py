# Simple in-memory abuse prevention control for per-user API request throttling

import time

from fastapi import HTTPException

from app.telemetry.logger import logger

from app.cache.redis_client import redis_client

RATE_LIMIT_WINDOW = 60
MAX_REQUESTS = 5

def check_rate_limit(identity: str, user: str):

    redis_key = f"rate_limit:{identity}"

    current_count = redis_client.get(redis_key)

    if current_count is None:

        redis_client.set(
            redis_key,
            1,
            ex=RATE_LIMIT_WINDOW
        )

        return

    current_count = int(current_count)

    if current_count >= MAX_REQUESTS:

        logger.warning(
            "\n🚨 RATE LIMIT EXCEEDED 🚨",
            user=user,
            request_count=current_count,
            limit=MAX_REQUESTS,
            window_seconds=RATE_LIMIT_WINDOW
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