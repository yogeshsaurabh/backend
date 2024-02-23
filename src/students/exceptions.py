from fastapi import HTTPException, status

NO_EMAIL_OR_PHONE_GIVEN = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="No email or phone number was provided.",
)

OTP_EXPIRY_NOT_SET = HTTPException(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    detail="No otp expiry was found while using OTP auth strategy.",
)

MAX_OTP_ATTEMPTS_REACHED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="max otp attempts reached.",
)
