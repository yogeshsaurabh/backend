from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from prisma.models import Student

from src.auth.email_service import EmailService
from src.auth.oauth import OAuthHandler
from src.auth.serializers import Token, UserRoles
from src.students.serializers import (
    EditStudent,
    EmailOTPReq,
    EmailOTPVerificationReq,
    OTPReq,
    OTPVerificationReq,
    WebOTPVerificationReq,
)
from src.students.service import StudentService
from src.students.utils import get_current_student

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/google-auth/signin")
async def google_auth_signup(token: Token) -> JSONResponse:
    auth_handler = OAuthHandler(Student, UserRoles.STUDENT)
    jwt_token: JSONResponse = await auth_handler.user_signup(token.token)
    return jwt_token


@router.post("/otp/send")
async def create_student_and_send_otp(otp_req: OTPReq):
    """Creates a student (if it does not exist) and sends OTP."""
    student_service = StudentService()
    new_student = await student_service.create_student_otp(otp_req.phone_number)
    # TODO: integrate 3rd party OTP service.
    return new_student


@router.post("/otp/verify")
async def verify_otp(otp_verification_req: OTPVerificationReq):
    student_service = StudentService()
    return await student_service.verify_otp(otp_verification_req)


@router.post("/email/otp/send")
async def create_student_and_email_otp(
    otp_req: EmailOTPReq,
    background_tasks: BackgroundTasks,
):
    otp, response = await StudentService().create_email_otp(otp_req.email)
    fast_mail, message, template_name = await EmailService().send_otp_email(
        otp=otp, email=otp_req.email
    )
    background_tasks.add_task(
        fast_mail.send_message, message, template_name=template_name
    )
    return response


@router.post("/email/otp/verify")
async def verify_email_otp(email_otp_verification_req: EmailOTPVerificationReq):
    return await StudentService().verify_email_otp(email_otp_verification_req)


@router.get("/web/otp")
async def get_web_otp(student_data: dict = Depends(get_current_student)):
    web_otp, expires_at = await StudentService().get_web_otp(student_data["id"])
    return {"otp": web_otp, "expires_at": expires_at}


@router.post("/web/otp/verify")
async def verify_web_otp(web_otp_verification_req: WebOTPVerificationReq):
    return await StudentService().verify_web_otp(web_otp_verification_req)


@router.get("/me")
async def get_student_details(student_token: dict = Depends(get_current_student)):
    student_id: int = student_token["id"]
    student_service = StudentService()
    student: Student = await student_service.get_student(student_id)
    return student


@router.patch("/")
async def edit_student(
    edit_req: EditStudent, student_data: dict = Depends(get_current_student)
):
    student_id: int = student_data["id"]
    return await StudentService().update_student(student_id, edit_req)
