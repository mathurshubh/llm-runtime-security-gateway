import pytest
from fastapi import HTTPException

from app.auth.jwt_auth import (
    authenticate_user,
    create_access_token,
    validate_jwt_token
)


def test_authenticate_admin():

    user = authenticate_user(
        "admin",
        "admin123"
    )

    assert user is not None
    assert user["role"] == "admin"


def test_authenticate_invalid_password():

    user = authenticate_user(
        "admin",
        "wrongpassword"
    )

    assert user is None


def test_authenticate_unknown_user():

    user = authenticate_user(
        "unknown",
        "password"
    )

    assert user is None


def test_create_access_token():

    token = create_access_token(
        {
            "sub": "admin",
            "role": "admin"
        }
    )

    assert isinstance(token, str)
    assert len(token) > 20


def test_validate_valid_token():

    token = create_access_token(
        {
            "sub": "admin",
            "role": "admin"
        }
    )

    result = validate_jwt_token(
        token
    )

    assert result["username"] == "admin"
    assert result["role"] == "admin"


def test_validate_invalid_token():

    with pytest.raises(
        HTTPException
    ):
        validate_jwt_token(
            "not.a.real.jwt"
        )