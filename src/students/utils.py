from fastapi import Depends

from src.auth.exceptions import ROLE_NOT_AUTHORIZED
from src.auth.jwt import JWTHelper
from src.auth.serializers import UserRoles
from src.auth.utils import get_current_user
from src.config import settings


class StudentRateLimitConfig:
    """Limits on login attempts for students."""

    MAX_WEB_LOGIN_ATTEMPTS = 100
    MAX_EMAIL_OTP_ATTEMPTS = 100
    MAX_PHONE_OTP_ATTEMPTS = 20
    MAX_ACTIVATION_ATTEMPTS = 100


def model_updated_response(success=True, msg=""):
    return {"status": "Success" if success else "Failed", "message": msg}


def email_otp_created_response(email: str, success=True):
    return {
        "status": "Success" if success else "Failed",
        "message": f"Verification OTP sent to {email}.",
    }


def phone_otp_created_response(phone_number: str, success=True):
    return {
        "status": "Success" if success else "Failed",
        "message": f"Verification OTP sent to +91 {phone_number}.",
    }


def get_current_student(token_data: dict = Depends(get_current_user)):
    if token_data["role"] != UserRoles.STUDENT:
        raise ROLE_NOT_AUTHORIZED

    return {
        "email": token_data["email"],
        "id": token_data["id"],
        "role": token_data["role"],
    }


def get_student_jwt(
    email: str,
    id: int,
    organization_id: int | None = None,
    refresh_token=True,
) -> dict[str, str]:
    jwt_helper = JWTHelper()
    role: str = UserRoles.STUDENT.value

    response: dict[str, str] = {
        "token": jwt_helper.create_token(
            email=email,
            id=id,
            role=role,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            organization_id=organization_id,
        )
    }

    if refresh_token:
        response["refresh_token"] = jwt_helper.create_token(
            email=email,
            id=id,
            role=role,
            expires_in=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            organization_id=organization_id,
        )

    return response
