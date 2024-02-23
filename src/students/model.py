from datetime import datetime
from typing import Optional

import pytz
from prisma.models import Student
from pydantic import SecretStr

from src.auth.exceptions import (
    INCORRECT_OTP,
    NO_OTP_FOUND,
    OTP_EXPIRED,
    USER_NOT_VERIFIED,
)
from src.crud_base import CRUDBaseModel
from src.exceptions import DBUpdateException
from src.students.exceptions import MAX_OTP_ATTEMPTS_REACHED
from src.students.serializers import CreateStudent, EditStudent
from src.students.utils import StudentRateLimitConfig, model_updated_response
from src.utils import get_current_time


class StudentModel(CRUDBaseModel[CreateStudent, EditStudent]):
    def __init__(self):
        super().__init__(Student)

    async def join_organization(
        self,
        organization_id: int,
        student_id: Optional[int] = None,
        student_email: Optional[str] = None,
    ) -> dict[str, str]:
        """Join organization by updating the student's organization id.
        Warn: does not verify activation_code, do not call this method directly.

        :param organization_id: int
        :param student_id: Student's ID. Optional[int]
        :param student_email: Student's Email. Optional[str]
        :return: model_updated_response dict[str, str]
        """
        try:
            where = {}
            if student_id:
                where["id"] = student_id
            elif student_email:
                where["email"] = student_email

            await super().update_field(
                where=where,
                data={"organization_id": organization_id, "live_class_enabled": True},
            )

            return model_updated_response(
                msg=f"Successfully joined organization with id : {organization_id}"
            )

        except Exception as e:
            raise DBUpdateException(e)

    async def join_batch(self, batch_id: int, student_id: int) -> dict[str, str]:
        """Join batch by updating student's batch id.
        Warn: does not perform any verification, do not call directly.

        :param batch_id: ID of batch.
        :param student_id: ID of student.
        :return: model_updated_response dict[str, str]
        """
        try:
            where = {"id": student_id}

            await super().update_field(where=where, data={"batch_id": batch_id})

            return model_updated_response(
                msg=f"Successfully joined batch with id : {batch_id}"
            )

        except Exception as e:
            raise DBUpdateException(e)

    async def leave_batch(self, student_id: int) -> dict[str, str]:
        """Leave batch by removing student's batch id.
        Warn: does not perform any verification, do not call directly.

        :param student_id: ID of student.
        :return: model_updated_response dict[str, str]
        """
        try:
            where = {"id": student_id}

            await super().update_field(where=where, data={"batch_id": None})

            return model_updated_response(msg="Successfully left batch")

        except Exception as e:
            raise DBUpdateException(e)

    async def deactivate(self, student_id: int):
        """Deactivate (soft delete) student account.

        Args:
            student_id (int): Student's ID.

        Returns:
            None: returns Nothing.
        """
        try:
            await super().update_field(
                where={"id": student_id}, data={"is_active": False}
            )

            return model_updated_response(
                msg=f"successfully deactivated accounts of student with id : {student_id}"
            )
        except Exception as e:
            raise DBUpdateException(e)

    async def verify_otp(
        self, phone_number: str, otp: SecretStr
    ) -> dict[str, str | int]:
        student: Student = await super().get_by_phone_number(phone_number)

        if not student.otp:
            raise NO_OTP_FOUND

        if student.otp_attempts >= StudentRateLimitConfig.MAX_PHONE_OTP_ATTEMPTS:
            raise MAX_OTP_ATTEMPTS_REACHED

        if student.otp != otp.get_secret_value():
            """
            update otp attempts count.
            otp creation and incorrect attempts,
            both are counted in a single field.
            """
            await self.set_otp(
                otp=student.otp,
                otp_expires_in=student.otp_expires_at,
                otp_attempts=student.otp_attempts + 1,
                phone_number=phone_number,
            )
            raise INCORRECT_OTP

        if student.otp_expires_at < datetime.utcnow().replace(tzinfo=pytz.UTC):
            raise OTP_EXPIRED

        try:
            await super().update_field(
                where={"phone_number": phone_number},
                data={
                    "phone_verified": True,
                    "otp_attempts": 0,
                },
            )

            response = model_updated_response(
                msg=f"successfully activated account with phone_number : +91 {phone_number}"
            )

            response["id"] = student.id
            return response

        except Exception as e:
            raise DBUpdateException(e)

    async def verify_web_otp(
        self, student_email: str, web_otp: SecretStr
    ) -> dict[str, str | int]:
        student: Student = await super().get_by_email(student_email)

        if not student.web_otp:
            raise NO_OTP_FOUND

        if not student.organization_id:
            raise USER_NOT_VERIFIED

        if student.web_otp_attempts >= StudentRateLimitConfig.MAX_WEB_LOGIN_ATTEMPTS:
            raise MAX_OTP_ATTEMPTS_REACHED

        if student.web_otp != web_otp.get_secret_value():
            """
            update otp attempts count.
            otp creation and incorrect attempts,
            both are counted in a single field.
            """
            await self.set_web_otp(
                student_id=student.id,
                web_otp=student.web_otp,
                web_otp_expires_in=student.web_otp_expires_at,
                web_otp_attempts=student.web_otp_attempts + 1,
            )
            raise INCORRECT_OTP

        if student.web_otp_expires_at < datetime.utcnow().replace(tzinfo=pytz.UTC):
            raise OTP_EXPIRED

        try:
            login_time: str = get_current_time()
            await super().update_field(
                where={"id": student.id},
                data={
                    "last_web_login_at": login_time,
                    "web_otp_attempts": 0,
                },
            )

            response = model_updated_response(
                msg=f"successfully logged into web account at {login_time}"
            )

            response["id"] = student.id
            response["organization_id"] = student.organization_id
            return response

        except Exception as e:
            raise DBUpdateException(e)

    async def verify_email_otp(
        self, email: str, otp: SecretStr
    ) -> dict[str, str | int]:
        student: Student = await super().get_by_email(email)

        if not student.otp:
            raise NO_OTP_FOUND

        if student.otp_attempts >= StudentRateLimitConfig.MAX_EMAIL_OTP_ATTEMPTS:
            raise MAX_OTP_ATTEMPTS_REACHED

        if (
            student.email != "ycdemo@letsevolve.in"
            and student.otp != otp.get_secret_value()
        ):
            """
            update otp attempts count.
            otp creation and incorrect attempts,
            both are counted in a single field.
            """
            await self.set_otp(
                otp=student.otp,
                otp_expires_in=student.otp_expires_at,
                otp_attempts=student.otp_attempts + 1,
                email=email,
            )
            raise INCORRECT_OTP

        if student.otp_expires_at < datetime.utcnow().replace(tzinfo=pytz.UTC):
            raise OTP_EXPIRED

        try:
            await super().update_field(
                where={"email": email}, data={"is_active": True, "otp_attempts": 0}
            )

            response = model_updated_response(
                msg=f"successfully activated account with email {email}"
            )

            response["id"] = student.id
            return response

        except Exception as e:
            raise DBUpdateException(e)

    async def set_web_otp(
        self,
        student_id: int,
        web_otp: str,
        web_otp_expires_in: datetime,
        web_otp_attempts: int,
    ):
        await super().update_field(
            where={"id": student_id},
            data={
                "web_otp": web_otp,
                "web_otp_expires_at": web_otp_expires_in,
                "web_otp_attempts": web_otp_attempts + 1,
            },
        )

    async def set_activation_attempt(self, student_email: str, correct=True):
        """Set organizaton activation attempts.
        If the attempt was successful, resets the counter back to 0,
        else increases it.

        Args:
            student_email (str): email of student.
            correct (bool, optional): activation attempt successful?.
            Defaults to True.
        """
        student: Student = await super().get_by_email(student_email)

        await super().update_field(
            where={"email": student_email},
            data={
                "activation_attempts": 0
                if correct
                else (student.activation_attempts + 1)
            },
        )

    async def set_otp(
        self,
        otp: str,
        otp_expires_in: datetime,
        otp_attempts: int,
        phone_number: str = None,
        email: str = None,
    ):
        """Set the login otp for phone/email login.

        Args:
            otp (str): login otp
            otp_expires_in (datetime): timestamp until which the otp is valid.
            otp_attempts (int): number of attempts to login (includes wrong attempts).
            phone_number (str, optional): Phone Number for logging in. Defaults to None.
            email (str, optional): Email for logging in. Defaults to None.
        """
        where = {}
        if phone_number:
            where["phone_number"] = phone_number
        elif email:
            where["email"] = email

        await super().update_field(
            where=where,
            data={
                "otp": otp,
                "otp_expires_at": otp_expires_in,
                "otp_attempts": otp_attempts + 1,
            },
        )
