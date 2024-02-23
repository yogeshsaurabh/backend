from datetime import datetime, timedelta
from secrets import randbelow

from src.auth.jwt import JWTHelper
from src.config import settings


class OTPHelper:
    OTP_LENGTH = 6

    @staticmethod
    def generate_otp() -> str:
        """Generate a 6 digit OTP."""
        digit_limit = 10

        otp = ""
        for _ in range(OTPHelper.OTP_LENGTH):
            otp += str(randbelow(digit_limit))

        return otp

    @staticmethod
    def create_expires_delta(minutes: int = settings.TIME_OUT_MINUTES):
        time_delta = timedelta(minutes=minutes)
        iso_datetime = (datetime.utcnow() + time_delta).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        return iso_datetime

    @staticmethod
    def get_phone_jwt(
            phone_number: str,
            id: int,
            role: str = "",
            organization_id: int | None = None,
            refresh_token=True,
    ) -> dict[str, str]:
        jwt_helper = JWTHelper()
        response: dict[str, str] = {
            "token": jwt_helper.create_token(
                id=id,
                role=role,
                phone_number=phone_number,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                organization_id=organization_id,
            )
        }

        if refresh_token:
            response["refresh_token"] = jwt_helper.create_token(
                id=id,
                role=role,
                phone_number=phone_number,
                expires_in=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
                organization_id=organization_id,
            )

        return response

    @staticmethod
    def get_email_jwt(
            email: str,
            id: int,
            role: str = "",
            organization_id: int | None = None,
            refresh_token=True,
    ) -> dict[str, str]:
        jwt_helper = JWTHelper()
        response: dict[str, str] = {
            "token": jwt_helper.create_token(
                id=id,
                role=role,
                email=email,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                organization_id=organization_id,
            )
        }

        if refresh_token:
            response["refresh_token"] = jwt_helper.create_token(
                id=id,
                role=role,
                email=email,
                expires_in=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
                organization_id=organization_id,
            )

        return response
