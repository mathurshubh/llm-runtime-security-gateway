# Redis client used for distributed rate limiting, security event storage, and shared gateway state.

import os
import redis


# Create a shared Redis connection used throughout the application.
# Connection settings can be overridden through environment variables.
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)