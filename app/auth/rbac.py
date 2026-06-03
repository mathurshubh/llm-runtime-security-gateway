# RBAC authorization utilities used to enforce role-based access controls on protected API endpoints.

from fastapi import Depends, HTTPException, status

from app.auth.jwt_auth import validate_jwt_token
from app.security.event_store import store_security_event


# Create a reusable authorization dependency that restricts endpoint access to a defined set of allowed roles.
def require_role(
    allowed_roles: list[str]
):

    def role_checker(
        api_user: dict = Depends(validate_jwt_token)
    ):

        user_role = api_user.get("role")

        # Record authorization failures for auditability, security analytics, and incident investigations.
        if user_role not in allowed_roles:

            store_security_event(
                event_type="authorization_denied",
                user=api_user["username"],
                details={
                    "user_role": user_role,
                    "allowed_roles": allowed_roles
                }
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return api_user

    return role_checker