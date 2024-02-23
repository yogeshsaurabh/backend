from datetime import datetime, timedelta

from jose import jwt

from src.auth.exceptions import JWT_KEY_NOT_FOUND, INFO_MISSING_FOR_JWT
from src.auth.serializers import UserRoles
from src.config import settings


class JWTHelper:
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES
    ALGORITHM = settings.ALGORITHM
    JWT_SECRET_KEY = settings.JWT_SECRET_KEY
    JWT_REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY
    JWT_ADMIN_SECRET_KEY = settings.JWT_ADMIN_SECRET_KEY

    def __init__(self, expires_in=None) -> None:
        """Create JWT tokens with expiry in minutes.

        Args:
            expires_in (int, optional): Minutes until token expires. Defaults to None.
        """
        expires_delta = datetime.utcnow()
        if expires_in is not None:
            expires_delta += timedelta(minutes=expires_in)
        else:
            expires_delta = datetime.utcnow() + timedelta(
                minutes=JWTHelper.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        self.expires_delta = expires_delta

    @staticmethod
    def create_expires_delta(minutes: float = settings.ACCESS_TOKEN_EXPIRE_MINUTES):
        time_delta = timedelta(minutes=minutes)
        return datetime.utcnow() + time_delta

    def create_token(
            self,
            id: int,
            role: str,
            email: str | None = None,
            phone_number: str | None = None,
            expires_in=None,
            organization_id: int | None = None,
    ) -> str:
        """Create JWT token for a user.

        Args:
            id (int): unique id of user, stored in DB.
            role (str): (UserRoles) different user roles like student, teacher, etc
            email optional(str): email of the user.
            phone_number optional(str): phone number of the user.
            expires_in (int, None): Minutes until token expires. Defaults to None.
            organization_id (int, None) Primary Key of Organization which user belongs to.

        Raises:
            RuntimeError: JWT secret key not found.
            RuntimeError: Both phone_number and email are missing, user_id or role is missing.

        Returns:
            str: JWT token string.
            :param organization_id:
            :param expires_in:
            :param phone_number:
            :param id:
            :param role:
            :param email:
        """
        if not JWTHelper.JWT_SECRET_KEY:
            raise JWT_KEY_NOT_FOUND
        if not (phone_number or email) or not (id and role):
            raise INFO_MISSING_FOR_JWT

        expires_delta = JWTHelper.create_expires_delta(expires_in) or self.expires_delta
        to_encode = {
            "exp": expires_delta,
            "id": id,
            "role": role,
            "organization_id": organization_id,
        }

        if phone_number:
            to_encode["phone_number"] = phone_number

        if email:
            to_encode["email"] = email

        encoded_jwt: str = jwt.encode(
            to_encode, JWTHelper.JWT_SECRET_KEY, JWTHelper.ALGORITHM
        )

        return encoded_jwt

    def create_admin_token(
            self,
            _id: int,
            expires_in: float = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    ) -> str:
        """Create JWT token for admin user.

        Args:
            _id (int): unique id of admin user, stored in DB.
            expires_in (int, None): Minutes until token expires. Defaults to None.

        Raises:
            RuntimeError: JWT secret key not found.

        Returns:
            str: JWT token string.
            :param exp:
            :param id:
            :param role:
        """
        if not JWTHelper.JWT_ADMIN_SECRET_KEY:
            raise JWT_KEY_NOT_FOUND
        if not _id:
            raise INFO_MISSING_FOR_JWT

        expires_delta = JWTHelper.create_expires_delta(expires_in) or self.expires_delta
        to_encode = {
            "exp": expires_delta,
            "id": _id,
            "role": UserRoles.ADMIN.value,
        }

        encoded_jwt: str = jwt.encode(
            to_encode, JWTHelper.JWT_ADMIN_SECRET_KEY, JWTHelper.ALGORITHM
        )

        return encoded_jwt
