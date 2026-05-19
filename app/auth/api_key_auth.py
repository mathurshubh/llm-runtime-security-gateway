from fastapi import Header, HTTPException

VALID_API_KEYS = {
    "test-key-123": "demo-user",
    "admin-key-456": "admin-user"
}


def validate_api_key(x_api_key: str = Header(...)):

    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    return {
        "api_key": x_api_key,
        "user": VALID_API_KEYS[x_api_key]
    }