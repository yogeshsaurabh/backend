from datetime import datetime

from prisma.models import Student

from src.auth.otp import OTPHelper
from src.auth.serializers import UserRoles
from src.exceptions import EmailNotFoundException, PhoneNumberNotFoundException
from src.students.exceptions import MAX_OTP_ATTEMPTS_REACHED
from src.students.model import StudentModel
from src.students.serializers import (
    CreateStudent,
    EditStudent,
    EmailOTPVerificationReq,
    OTPVerificationReq,
    WebOTPVerificationReq,
)
from src.students.utils import (
    StudentRateLimitConfig,
    email_otp_created_response,
    phone_otp_created_response,
    get_student_jwt,
)


def delete_secrets(student: Student):
    if hasattr(student, "otp"):
        del student.otp

    if hasattr(student, "activation_code"):
        del student.activation_code

    return student


class StudentService:
    def __init__(self) -> None:
        self.model = StudentModel()

    async def create_student(self, student_data: CreateStudent):
        # create an instance of the student database model
        new_student = await self.model.create(student_data)
        return new_student

    async def create_student_otp(self, phone_number: str):
        """
        Create a new student with OTP verification.
        If student already exists, creates a new OTP.
        """
        otp: str = OTPHelper.generate_otp()
        otp_expires_in: datetime = OTPHelper.create_expires_delta()

        try:
            existing_student = await self.get_student_by_phone_number(phone_number)
            otp_count: int = existing_student.otp_attempts

            if otp_count >= StudentRateLimitConfig.MAX_PHONE_OTP_ATTEMPTS:
                raise MAX_OTP_ATTEMPTS_REACHED

            await self.model.set_otp(
                phone_number=phone_number,
                otp=otp,
                otp_expires_in=otp_expires_in,
                otp_attempts=otp_count,
            )

            return phone_otp_created_response(phone_number=phone_number)
        except PhoneNumberNotFoundException:
            print(f"student with ph: {phone_number} not found, creating new.")

        student_data = CreateStudent(
            phone_number=phone_number, otp=otp, otp_expires_at=otp_expires_in
        )

        await self.create_student(student_data)

        return phone_otp_created_response(phone_number=phone_number)

    async def create_email_otp(self, email: str):
        """
        Create a new student with OTP verification.
        If student already exists, creates a new OTP.
        """
        otp: str = OTPHelper.generate_otp()
        otp_expires_in: datetime = OTPHelper.create_expires_delta()

        GUEST_ACCOUNT_OTP: str = "071123"
        GUEST_ACCOUNT_EMAIL: str = "guest@letsevolve.in"

        if email == GUEST_ACCOUNT_EMAIL:
            otp = GUEST_ACCOUNT_OTP

        try:
            existing_student = await self.get_student_by_email(email)

            otp_count: int = existing_student.otp_attempts

            if otp_count >= StudentRateLimitConfig.MAX_EMAIL_OTP_ATTEMPTS:
                raise MAX_OTP_ATTEMPTS_REACHED

            await self.model.set_otp(
                email=email,
                otp=otp,
                otp_expires_in=otp_expires_in,
                otp_attempts=otp_count,
            )

            return otp, email_otp_created_response(email=email)

        except EmailNotFoundException:
            print(f"student with email: {email} not found, creating new.")

        student_data = CreateStudent(
            email=email, otp=otp, otp_expires_at=otp_expires_in
        )

        await self.create_student(student_data)
        return otp, email_otp_created_response(email=email)

    async def get_web_otp(self, student_id: int) -> tuple[str, datetime]:
        """
        Create a web auth OTP.
        """
        web_otp: str = OTPHelper.generate_otp()
        web_otp_expires_at: datetime = OTPHelper.create_expires_delta()
        student: Student = await self.model.get(student_id)
        web_otp_count: int = student.web_otp_attempts

        if web_otp_count >= StudentRateLimitConfig.MAX_WEB_LOGIN_ATTEMPTS:
            raise MAX_OTP_ATTEMPTS_REACHED

        await self.model.set_web_otp(
            student_id=student_id,
            web_otp=web_otp,
            web_otp_expires_in=web_otp_expires_at,
            web_otp_attempts=web_otp_count,
        )
        return web_otp, web_otp_expires_at

    async def get_student(self, student_id: int) -> Student:
        where = {"id": student_id}
        include = {"Organization": False}
        student: Student = await self.model.get_unique(where, include)
        delete_secrets(student)
        return student

    async def get_student_by_email(self, email: str) -> Student:
        student: Student = await self.model.get_by_email(email)
        return student

    async def get_student_by_phone_number(self, phone_number: str) -> Student:
        student: Student = await self.model.get_by_phone_number(phone_number)
        return student

    async def verify_email_otp(self, verification_req: EmailOTPVerificationReq):
        response_msg = await self.model.verify_email_otp(
            email=verification_req.email, otp=verification_req.otp
        )

        student_id: int = response_msg["id"]
        tokens: dict[str, str] = OTPHelper().get_email_jwt(
            id=student_id,
            email=verification_req.email,
            role=UserRoles.STUDENT.value,
        )

        response_msg["token"] = tokens["token"]
        response_msg["refresh_token"] = tokens["refresh_token"]
        del response_msg["id"]
        return response_msg

    async def verify_otp(self, verification_req: OTPVerificationReq):
        response_msg = await self.model.verify_otp(
            phone_number=verification_req.phone_number, otp=verification_req.otp
        )
        student_id: int = response_msg["id"]
        tokens: dict[str, str] = OTPHelper().get_phone_jwt(
            id=student_id,
            phone_number=verification_req.phone_number,
            role=UserRoles.STUDENT.value,
        )

        response_msg["token"] = tokens["token"]
        response_msg["refresh_token"] = tokens["refresh_token"]
        del response_msg["id"]
        return response_msg

    async def verify_web_otp(self, verification_req: WebOTPVerificationReq):
        response_msg = await self.model.verify_web_otp(
            student_email=verification_req.student_email,
            web_otp=verification_req.web_otp,
        )
        student_id: int = response_msg["id"]
        organization_id: int = response_msg["organization_id"]

        tokens: dict[str, str] = get_student_jwt(
            id=student_id,
            email=verification_req.student_email,
            organization_id=organization_id,
        )

        response_msg["token"] = tokens["token"]
        response_msg["refresh_token"] = tokens["refresh_token"]
        del response_msg["id"]
        return response_msg

    async def update_student(self, student_id: int, student_edit: EditStudent):
        student = await self.get_student(student_id)

        if hasattr(student_edit, "profile") and student_edit.profile is not None:
            student_edit.profile = student_edit.profile.json(exclude_unset=True)

        updated_student = await self.model.update(student.id, student, student_edit)
        delete_secrets(updated_student)
        return updated_student

    async def deactivate_account(self, student_id: int) -> dict[str, str] | None:
        deleted_student: dict[str, str] | None = await self.model.deactivate(student_id)
        return deleted_student

    async def delete_student(self, email: str) -> dict[str, str] | None:
        deleted_student: dict[str, str] | None = await self.model.remove_by_email(email)
        return deleted_student
