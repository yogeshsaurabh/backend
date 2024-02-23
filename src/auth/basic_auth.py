from typing import Generic, Type, TypeVar

from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from pydantic import BaseModel, SecretStr

from src.admins.serializers import CreateAdminReq
from src.admins.service import AdminService
from src.auth.exceptions import (
    RoleNotAllowedException,
    CREDENTIALS_EXCEPTION,
    USER_NOT_VERIFIED,
    USER_NOT_ACTIVE,
    USER_NOT_FOUND
)
from src.auth.jwt import JWTHelper
from src.auth.serializers import UserRoles, LoginReq, EmailLoginReq
from src.config import settings
from src.teachers.serializers import CreateTeacherReq
from src.teachers.service import TeacherService
from src.teachers.utils import get_teacher_jwt

ModelType = TypeVar("ModelType", bound=BaseModel)


class BasicAuthHandler(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], role: UserRoles) -> None:
        """
        BasicAuth object with default methods to authenticate and verify a user.

        **Parameters**

        * `model`: A Prisma model

        """
        self.model: Type[ModelType] = model
        self.user_type: str = role.value
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def find_user_by_username(self, username: str) -> Type[ModelType] | None:
        user: Type[ModelType] | None = await self.model.prisma().find_unique(
            where={"username": username}, include={}
        )
        return user

    async def find_user_by_email(self, email: str) -> Type[ModelType] | None:
        user: Type[ModelType] | None = await self.model.prisma().find_unique(
            where={"email": email}, include={}
        )
        return user

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: SecretStr, hashed_password: str):
        return self.pwd_context.verify(plain_password.get_secret_value(), hashed_password)

    async def admin_login(self, login_req: LoginReq):
        username: str = login_req.username
        password: SecretStr = login_req.password

        user: Type[ModelType] = await self.find_user_by_username(username)

        if not self.verify_password(plain_password=password, hashed_password=user.password):
            raise CREDENTIALS_EXCEPTION

        if not user.is_verified:
            raise USER_NOT_VERIFIED

        return self.get_admin_jwt(_id=user.id)

    async def teacher_login(self, login_req: EmailLoginReq):
        email: str = login_req.email
        password: SecretStr = login_req.password

        user: Type[ModelType] = await self.find_user_by_email(email)

        if not user:
            raise USER_NOT_FOUND

        if not self.verify_password(plain_password=password, hashed_password=user.password):
            raise CREDENTIALS_EXCEPTION

        if not user.phone_verified:
            raise USER_NOT_VERIFIED

        if not user.is_active:
            raise USER_NOT_ACTIVE

        return get_teacher_jwt(_id=user.id, email=user.email, phone_number=user.phone_number)

    async def admin_signup(self, admin_signup_req: CreateAdminReq):
        if self.user_type != UserRoles.ADMIN.value:
            raise RoleNotAllowedException(self.user_type)

        hashed_password: str = self.get_password_hash(admin_signup_req.password.get_secret_value())
        admin_signup_req.password = SecretStr(hashed_password)
        admin_service = AdminService()
        new_admin = await admin_service.create_admin(admin_signup_req)
        del new_admin.password
        return new_admin

    async def teacher_signup(self, teacher_signup_req: CreateTeacherReq):
        if self.user_type != UserRoles.TEACHER.value:
            raise RoleNotAllowedException(self.user_type)

        hashed_password: str = self.get_password_hash(teacher_signup_req.password.get_secret_value())
        teacher_signup_req.password = SecretStr(hashed_password)
        teacher_service = TeacherService()
        new_teacher = await teacher_service.create_teacher(teacher_signup_req)
        del new_teacher.password
        return new_teacher

    @staticmethod
    def get_admin_jwt(_id: int, refresh_token=True) -> JSONResponse:
        jwt_helper = JWTHelper()
        response: dict[str, str] = {
            "token": jwt_helper.create_admin_token(_id=_id)
        }

        if refresh_token:
            response["refresh_token"] = jwt_helper.create_admin_token(
                _id=_id,
                expires_in=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            )

        return JSONResponse(response)
