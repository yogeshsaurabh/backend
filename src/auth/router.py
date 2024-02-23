from fastapi import APIRouter
from fastapi.responses import JSONResponse
from prisma.models import Admin as AdminModel, Teacher as TeacherModel

from src.admins.serializers import TokenPayload as AdminTokenPayload
from src.auth.basic_auth import BasicAuthHandler
from src.auth.exceptions import ROLE_NOT_AUTHORIZED
from src.auth.oauth import OAuthHandler
from src.auth.serializers import Token, LoginReq, TokenPayload, EmailLoginReq
from src.auth.serializers import UserRoles
from src.auth.utils import decode_token, decode_admin_token
from src.students.serializers import TokenPayload as StudentTokenPayload
from src.teachers.utils import get_teacher_jwt

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/student/token")
async def get_student_token(refresh_token: Token) -> JSONResponse:
    """Get a JWT token from refresh token. \n
        Auth Strategy: OAuth \n
        Warn: Refresh Tokens obtained using phone number won't work.

    Args:
        refresh_token (str): refresh token

    Returns:
        JSONResponse: JWT token
    """
    token_payload: StudentTokenPayload = decode_token(refresh_token.token)
    email: str = token_payload.email
    _id: int = token_payload.id
    role: str = token_payload.role.value
    organization_id: str | None = token_payload.organization_id

    new_token: dict[str, str] = OAuthHandler.get_jwt(
        email=email,
        id=_id,
        role=role,
        refresh_token=False,
        organization_id=organization_id,
    )

    return JSONResponse(new_token)


@router.post("/admin/token")
async def admin_user_get_token(refresh_token: Token) -> JSONResponse:
    """Get a JWT token from refresh token.

    Args:
        refresh_token (str): refresh token

    Returns:
        JSONResponse: JWT token
    """
    token_payload: AdminTokenPayload = decode_admin_token(refresh_token.token)
    role: UserRoles = token_payload.role
    basic_auth_handler = BasicAuthHandler(AdminModel, role)
    return basic_auth_handler.get_admin_jwt(_id=token_payload.id, refresh_token=False)


@router.post("/teacher/token")
async def get_teacher_token(refresh_token: Token) -> dict[str, str]:
    """Get a JWT token from refresh token.

    Args:
        refresh_token (str): refresh token

    Returns:
        JSONResponse: JWT token
    """
    token_payload: TokenPayload = decode_token(refresh_token.token)
    role: UserRoles = token_payload.role

    if role != UserRoles.TEACHER:
        raise ROLE_NOT_AUTHORIZED

    return get_teacher_jwt(_id=token_payload.id, email=token_payload.email, phone_number=token_payload.phone_number,
                           refresh_token=False)


@router.post("/admin/login")
async def admin_login(admin_login_req: LoginReq):
    """Login route for the admin user. \n
        AuthStrategy: Basic \n
        UserType: Admin \n

    :param admin_login_req:
    :return:
    """
    basic_auth_handler = BasicAuthHandler(AdminModel, UserRoles.ADMIN)
    new_token: JSONResponse = await basic_auth_handler.admin_login(admin_login_req)

    return new_token


@router.post("/teacher/login")
async def teacher_login(teacher_login_req: EmailLoginReq):
    """Login route for the teacher user. \n
        AuthStrategy: Basic \n
        UserType: Teacher \n

    :param teacher_login_req:
    :return:
    """
    basic_auth_handler = BasicAuthHandler(TeacherModel, UserRoles.TEACHER)
    new_token: JSONResponse = await basic_auth_handler.teacher_login(teacher_login_req)

    return new_token
