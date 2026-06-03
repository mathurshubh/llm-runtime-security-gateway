# JWT-based authentication utilities responsible for password verification, token issuance, and identity validation.

from datetime import datetime, timedelta, timezone
import os

from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer

from passlib.context import CryptContext


# Signing key used to issue and validate JWT access tokens.
# Production deployments should load this from a secure secret store.
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "super-secret-development-key"
)

# JWT signing algorithm used for token generation and validation.
ALGORITHM = "HS256"

# Access token lifetime in minutes.
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# OAuth2 bearer token handler
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


# Demo identity store used for local development and testing.
# Production systems would integrate with an external identity provider.
fake_users_db = {

    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin"
    },

    "analyst": {
        "username": "analyst",
        "hashed_password": pwd_context.hash("analyst123"),
        "role": "analyst"
    },

    "user": {
        "username": "user",
        "hashed_password": pwd_context.hash("user123"),
        "role": "user"
    }
}

# Verify a plaintext password against a stored bcrypt hash.
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

# Authenticate user credentials and return the associated identity record.
def authenticate_user(
    username: str,
    password: str
) -> dict | None:

    user = fake_users_db.get(username)

    if not user:
        return None

    if not verify_password(
        password,
        user["hashed_password"]
    ):
        return None

    return user

# Generate a signed JWT access token containing identity and authorization claims used by downstream services.
def create_access_token(
    data: dict
) -> str:
    
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

# Validate JWT authenticity, expiration, and required claims before allowing access to protected resources.
def validate_jwt_token(
    token: str = Depends(oauth2_scheme)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token"
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        role = payload.get("role")
        
        if not username or not role:
            raise credentials_exception

        return {
            "username": username,
            "role": role
        }

    except JWTError:
        raise credentials_exception