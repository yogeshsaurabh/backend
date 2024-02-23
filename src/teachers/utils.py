from fastapi import Depends

from src.auth.exceptions import ROLE_NOT_AUTHORIZED
from src.auth.jwt import JWTHelper
from src.auth.serializers import UserRoles
from src.auth.utils import get_current_user
from src.config import settings


def model_updated_response(success=True, msg=""):
    return {
        "status": "Success" if success else "Failed",
        "message": msg
    }


def get_current_teacher(token_data: dict = Depends(get_current_user)):
    if token_data["role"] != UserRoles.TEACHER:
        raise ROLE_NOT_AUTHORIZED

    return {
        "email": token_data["email"],
        "id": token_data["id"],
        "role": token_data["role"],
    }


def get_teacher_jwt(
        _id: int,
        email: str,
        phone_number: str,
        refresh_token=True,
) -> dict[str, str]:
    jwt_helper = JWTHelper()
    role: str = UserRoles.TEACHER.value

    response: dict[str, str] = {
        "token": jwt_helper.create_token(
            id=_id,
            role=role,
            email=email,
            phone_number=phone_number,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    }

    if refresh_token:
        response["refresh_token"] = jwt_helper.create_token(
            id=_id,
            role=role,
            email=email,
            phone_number=phone_number,
            expires_in=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        )

    return response
