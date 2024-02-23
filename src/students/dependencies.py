from fastapi import Depends

from src.auth.utils import get_current_user
from src.auth.exceptions import ROLE_NOT_AUTHORIZED
from src.auth.serializers import UserRoles


def get_current_student(token_data: dict = Depends(get_current_user)):
    if token_data["role"] != UserRoles.STUDENT:
        raise ROLE_NOT_AUTHORIZED

    token = {
        "id": token_data["id"],
        "role": token_data["role"],
    }

    if token_data.get("email") is not None:
        token["email"] = token_data["email"]

    if token_data.get("phone_number") is not None:
        token["phone_number"] = token_data["phone_number"]

    return token
