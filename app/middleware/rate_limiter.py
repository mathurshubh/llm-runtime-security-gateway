import time
from fastapi import HTTPException

from app.telemetry.logger import logger

RATE_LIMIT_WINDOW = 60
MAX_REQUESTS = 5

request_store = {}


def check_rate_limit(api_key: str):

    current_time = time.time()

    if api_key not in request_store:
        request_store[api_key] = []

    request_store[api_key] = [
        timestamp
        for timestamp in request_store[api_key]
        if current_time - timestamp < RATE_LIMIT_WINDOW
    ]

    if len(request_store[api_key]) >= MAX_REQUESTS:

        logger.warning(
            "\n🚨 RATE LIMIT EXCEEDED 🚨",
            api_key=api_key
        )
        
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )

    request_store[api_key].append(current_time)
