import pytest
from fastapi import HTTPException

from app.auth.rbac import require_role


def test_admin_allowed():

    checker = require_role(
        ["admin"]
    )

    result = checker(
        {
            "username": "admin",
            "role": "admin"
        }
    )

    assert result["role"] == "admin"


def test_analyst_allowed():

    checker = require_role(
        ["admin", "analyst"]
    )

    result = checker(
        {
            "username": "analyst",
            "role": "analyst"
        }
    )

    assert result["role"] == "analyst"


def test_user_denied():

    checker = require_role(
        ["admin"]
    )

    with pytest.raises(
        HTTPException
    ):

        checker(
            {
                "username": "user",
                "role": "user"
            }
        )


def test_admin_denied_when_user_required():

    checker = require_role(
        ["user"]
    )

    with pytest.raises(
        HTTPException
    ):

        checker(
            {
                "username": "admin",
                "role": "admin"
            }
        )