from pathlib import Path
from typing import Any, Dict
from typing import List

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel

from src.config import settings


class EmailSchema(BaseModel):
    email: List[EmailStr]
    body: Dict[str, Any]


class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_USERNAME,
            MAIL_PORT=587,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME="Evolve Support",
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            TEMPLATE_FOLDER=Path(__file__).parent / "templates",
        )

    async def send_otp_email(self, email: str, otp: str):
        email_schema = EmailSchema(email=[email], body={"otp": otp})
        message = MessageSchema(
            subject="Your One-Time Password (OTP) for Evolve",
            recipients=email_schema.email,
            template_body=email_schema.body,
            subtype=MessageType.html,
        )

        fm = FastMail(self.conf)

        template_name = "email_otp.html"
        return fm, message, template_name

    async def send_activation_code_email(self, email: str, code: str):
        email_schema = EmailSchema(email=[email], body={"activation_code": code})
        message = MessageSchema(
            subject="Your activation code for Evolve",
            recipients=email_schema.email,
            template_body=email_schema.body,
            subtype=MessageType.html,
        )

        fm = FastMail(self.conf)

        template_name = "activation_code.html"
        return fm, message, template_name
