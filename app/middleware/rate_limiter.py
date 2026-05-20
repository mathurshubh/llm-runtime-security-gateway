import time

from fastapi import HTTPException

from app.telemetry.logger import logger

RATE_LIMIT_WINDOW = 60
MAX_REQUESTS = 5

request_store = {}


def check_rate_limit(api_key: str, user: str):

    current_time = time.time()

    if api_key not in request_store:
        request_store[api_key] = []

    # Keep only requests inside time window
    request_store[api_key] = [
        timestamp
        for timestamp in request_store[api_key]
        if current_time - timestamp < RATE_LIMIT_WINDOW
    ]

    current_request_count = len(request_store[api_key])

    if current_request_count >= MAX_REQUESTS:

        logger.warning(
            "\n🚨 RATE LIMIT EXCEEDED 🚨",
            user=user,
            api_key=api_key,
            request_count=current_request_count,
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

    request_store[api_key].append(current_time)