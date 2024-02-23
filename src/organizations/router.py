from fastapi import APIRouter, Depends, BackgroundTasks
from prisma.models import Organization, Student, Batch

from src.auth.utils import get_current_admin
from src.auth.email_service import EmailService
from src.organizations.activation_codes.serializers import CreateActivationCode
from src.organizations.activation_codes.service import ActivationCodeService
from src.organizations.batches.serializers import (
    AddStudentToBatchReq,
    RemoveStudentFromBatchReq,
    CreateBatch,
)
from src.organizations.batches.service import BatchService
from src.organizations.serializers import (
    AddStudentToOrganizationReq,
    CreateOrganization,
    EditOrganization,
    JoinOrganizationReq,
)
from src.organizations.exceptions import MAX_JOINING_ATTEMPTS
from src.organizations.service import OrganizationService
from src.students.model import StudentModel
from src.students.service import StudentService
from src.students.utils import get_current_student, StudentRateLimitConfig

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/create")
async def create_new_organization(
    create_org_req: CreateOrganization, _: dict = Depends(get_current_admin)
):
    new_organization: Organization = await OrganizationService().create(create_org_req)
    return new_organization


@router.get("/{organization_id}")
async def get_organization(organization_id: int, _: dict = Depends(get_current_admin)):
    organization: Organization = await OrganizationService().get(organization_id)
    return organization


@router.get("/")
async def get_organization_by_name(
    organization_name: str, _: dict = Depends(get_current_admin)
):
    organization: Organization = await OrganizationService().get_org_by_name(
        organization_name
    )
    return organization


@router.patch("/{organization_id}")
async def edit_organization(
    organization_id: int,
    edit_org_req: EditOrganization,
    _: dict = Depends(get_current_admin),
):
    updated_organization: Organization = (
        await OrganizationService().update_organization(organization_id, edit_org_req)
    )
    return updated_organization


@router.post("/activation_code/new")
async def create_activation_code(
    data: CreateActivationCode,
    background_tasks: BackgroundTasks,
    _: dict = Depends(get_current_admin),
):
    activation_code, response = await ActivationCodeService().create(data)
    fast_mail, message, template_name = await EmailService().send_activation_code_email(
        email=response.student_email, code=activation_code
    )
    background_tasks.add_task(
        fast_mail.send_message, message, template_name=template_name
    )
    return response


@router.get("/activation_code/all")
async def fetch_all_codes(
    skip: int = 0, limit: int = 10, _: dict = Depends(get_current_admin)
):
    return await ActivationCodeService().get_all(skip, limit)


@router.post("/add/student")
async def add_student_to_organization(
    add_student_req: AddStudentToOrganizationReq, _: dict = Depends(get_current_admin)
):
    organization_service = OrganizationService()
    return await organization_service.add_student_to_organization(add_student_req)


@router.post("/batch/create")
async def create_new_batch(
    create_batch_req: CreateBatch, _: dict = Depends(get_current_admin)
):
    batch_service = BatchService()
    new_batch: Batch = await batch_service.create(create_batch_req)
    return new_batch


@router.post("/batch/add/student")
async def add_student_to_batch(
    add_student_to_batch_req: AddStudentToBatchReq, _: dict = Depends(get_current_admin)
):
    batch_service = BatchService()
    student_id: int = add_student_to_batch_req.student_id
    batch_id: int = add_student_to_batch_req.batch_id
    return await batch_service.add_student_to_batch(student_id, batch_id)


@router.post("/batch/remove/student")
async def remove_student_from_batch(
    remove_student_from_batch_req: RemoveStudentFromBatchReq,
    _: dict = Depends(get_current_admin),
):
    student_id: int = remove_student_from_batch_req.student_id
    return await StudentModel().leave_batch(student_id)


@router.post("/join/student")
async def join_organization(
    join_req: JoinOrganizationReq, student_token: dict = Depends(get_current_student)
):
    organization_service = OrganizationService()
    student: Student = await StudentService().get_student(student_token["id"])

    if student.activation_attempts >= StudentRateLimitConfig.MAX_ACTIVATION_ATTEMPTS:
        raise MAX_JOINING_ATTEMPTS

    add_student_req: AddStudentToOrganizationReq = AddStudentToOrganizationReq(
        **join_req.dict(exclude_unset=True), student_email=student.email
    )
    return await organization_service.add_student_to_organization(add_student_req)
