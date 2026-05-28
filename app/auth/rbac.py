from fastapi import Depends, HTTPException, status

from app.auth.jwt_auth import validate_jwt_token


def require_role(allowed_roles: list):

    def role_checker(
        api_user: dict = Depends(validate_jwt_token)
    ):

        user_role = api_user.get("role")

        if user_role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return api_user

    return role_checker