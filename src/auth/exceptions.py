from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class RoleNotAllowedException(HTTPException):
    def __init__(self, role: str):
        super().__init__(
            status.HTTP_401_UNAUTHORIZED, f'role "{role}" is not a valid OAuth role.'
        )


class UndefinedUserTypeException(HTTPException):
    def __init__(self, user_type: str):
        super().__init__(
            status.HTTP_401_UNAUTHORIZED, f"Undefined User Type {user_type}"
        )


class GoogleAuthException(HTTPException):
    def __init__(self, msg: str):
        super().__init__(
            status.HTTP_500_INTERNAL_SERVER_ERROR, f"Google Auth Error - {msg}"
        )


class IncorrectActivationCodeException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, "Activation code is incorrect.")


CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

TOKEN_EXPIRED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token expired",
    headers={"WWW-Authenticate": "Bearer"},
)

USER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Could not find user",
)

USER_NOT_VERIFIED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User is not verified.",
)

USER_NOT_ACTIVE = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User is not active.",
)

ROLE_NOT_AUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Role Not Authorized",
)

UNAUTHORIZED_ACCESS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not Authorized to access this resource",
)

NO_OTP_FOUND = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="no otp found for student."
)

NO_ACTIVATION_CODE_FOUND = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="no activation code found."
)

INCORRECT_OTP = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="OTP is incorrect."
)

OTP_EXPIRED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired."
)

JWT_KEY_NOT_FOUND = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No JWT Key found."
)

INFO_MISSING_FOR_JWT = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="TOKEN NOT CREATED: PHONE NUMBER/EMAIL/ID/ROLE missing",
)
