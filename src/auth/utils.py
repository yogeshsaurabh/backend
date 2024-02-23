from datetime import datetime

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError

from src.admins.serializers import TokenPayload as AdminTokenPayload
from src.auth.exceptions import (
    CREDENTIALS_EXCEPTION,
    JWT_KEY_NOT_FOUND,
    ROLE_NOT_AUTHORIZED,
    TOKEN_EXPIRED,
    USER_NOT_FOUND,
)
from src.auth.serializers import TokenPayload, UserRoles
from src.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def decode_token(token: str) -> TokenPayload:
    jwt_secret_key: str | None = settings.JWT_SECRET_KEY
    if not jwt_secret_key:
        raise JWT_KEY_NOT_FOUND

    try:
        payload = jwt.decode(
            token,
            jwt_secret_key,
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise TOKEN_EXPIRED
        return token_data
    except (JWTError, ValidationError):
        raise CREDENTIALS_EXCEPTION


def decode_admin_token(token: str) -> AdminTokenPayload:
    jwt_secret_key: str | None = settings.JWT_ADMIN_SECRET_KEY
    if not jwt_secret_key:
        raise JWT_KEY_NOT_FOUND

    try:
        payload = jwt.decode(
            token,
            jwt_secret_key,
            algorithms=[settings.ALGORITHM],
        )
        token_data = AdminTokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise TOKEN_EXPIRED
        return token_data
    except (JWTError, ValidationError):
        raise CREDENTIALS_EXCEPTION


def get_current_user(token: str = Depends(oauth2_scheme)):
    token_data: TokenPayload = decode_token(token)

    if token_data is None:
        raise USER_NOT_FOUND

    user_data = {
        "id": token_data.id,
        "role": token_data.role,
    }

    if hasattr(token_data, "email"):
        user_data["email"] = token_data.email

    if hasattr(token_data, "phone_number"):
        user_data["phone_number"] = token_data.phone_number

    if hasattr(token_data, "organization_id"):
        user_data["organization_id"] = token_data.organization_id

    return user_data


def get_current_admin(token: str = Depends(oauth2_scheme)):
    token_data: AdminTokenPayload = decode_admin_token(token)

    if token_data is None:
        raise USER_NOT_FOUND

    if token_data.role != UserRoles.ADMIN:
        raise ROLE_NOT_AUTHORIZED

    user_data = {
        "id": token_data.id,
        "role": token_data.role,
    }

    return user_data
