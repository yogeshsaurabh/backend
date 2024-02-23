from datetime import datetime
from typing import Optional

from pydantic import BaseModel, SecretStr, root_validator

from src.auth.serializers import UserRoles
from src.students.exceptions import NO_EMAIL_OR_PHONE_GIVEN, OTP_EXPIRY_NOT_SET


def verify_email_or_phone_present(_, values):
    """Either email or phone number must be present"""
    email = values.get("email")
    phone_number = values.get("phone_number")

    if not (email or phone_number):
        raise NO_EMAIL_OR_PHONE_GIVEN

    return values


def verify_otp_and_expiry_present(_, values):
    """Verify OTP expiry is present if OTP is set."""
    otp: Optional[SecretStr] = values.get("opt")
    otp_expires_at: Optional[datetime] = values.get("otp_expires_at")

    if otp and not otp_expires_at:
        raise OTP_EXPIRY_NOT_SET

    return values


class Profile(BaseModel):
    phone_number: str
    phone_number_owner: str
    qualification: str
    instituteName: Optional[str]
    heardAboutUsFrom: str
    profilePictureURL: Optional[str]
    financialAspirations: list[str]
    careerAspirations: list[str]


class CreateStudent(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    age: Optional[int]
    otp: Optional[SecretStr]
    otp_expires_at: Optional[datetime]
    profile: Optional[Profile] = None

    _auth_strategy_validation = root_validator(allow_reuse=True)(
        verify_email_or_phone_present
    )

    _otp_expiry_validation = root_validator(allow_reuse=True)(
        verify_otp_and_expiry_present
    )

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}


class EditStudent(BaseModel):
    name: Optional[str]
    age: Optional[int]
    profile: Optional[Profile]


class TokenPayload(BaseModel):
    id: int
    exp: int
    email: Optional[str]
    phone_number: Optional[str]
    role: UserRoles
    organization_id: Optional[int]

    _auth_strategy_validation = root_validator(allow_reuse=True)(
        verify_email_or_phone_present
    )


class GoogleSignIn(BaseModel):
    name: str
    email: str


class OTPReq(BaseModel):
    phone_number: str


class OTPVerificationReq(BaseModel):
    phone_number: str
    otp: SecretStr


class EmailOTPReq(BaseModel):
    email: str


class EmailOTPVerificationReq(BaseModel):
    email: str
    otp: SecretStr


class WebOTPVerificationReq(BaseModel):
    student_email: str
    web_otp: SecretStr
