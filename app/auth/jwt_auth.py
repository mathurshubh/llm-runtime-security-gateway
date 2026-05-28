from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer

from passlib.context import CryptContext


# JWT secret key
SECRET_KEY = "super-secret-development-key"

# JWT signing algorithm
ALGORITHM = "HS256"

# Token expiration
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


# Demo users database
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin"
    }
}


def verify_password(
    plain_password,
    hashed_password
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def authenticate_user(
    username,
    password
):

    user = fake_users_db.get(username)

    if not user:
        return None

    if not verify_password(
        password,
        user["hashed_password"]
    ):
        return None

    return user


def create_access_token(data: dict):

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

        if not username:
            raise credentials_exception

        return {
            "username": username,
            "role": role
        }

    except JWTError:
        raise credentials_exception