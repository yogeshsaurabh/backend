from prisma.models import ActivationCode, Organization

from src.auth.exceptions import IncorrectActivationCodeException
from src.organizations.activation_codes.model import ActivationCodeModel
from src.organizations.model import OrganizationModel
from src.organizations.serializers import (
    AddStudentToOrganizationReq,
    CreateOrganization,
    EditOrganization,
)
from src.students.model import StudentModel


class OrganizationService:
    def __init__(self) -> None:
        self.model = OrganizationModel()

    async def create(self, organization: CreateOrganization):
        new_organization: Organization = await self.model.create(organization)
        return new_organization

    async def get(self, organization_id: int):
        organization: Organization = await self.model.get(organization_id)
        return organization

    async def get_org_by_name(self, organization_name: str):
        organization: Organization = await self.model.get_by_name(organization_name)
        return organization

    async def update_organization(
        self, organization_id: int, edit_organization_req: EditOrganization
    ):
        organization: Organization = await self.get(organization_id)
        updated_organization: Organization = await self.model.update(
            organization_id, organization, edit_organization_req
        )
        return updated_organization

    async def add_student_to_organization(
        self, add_student_req: AddStudentToOrganizationReq
    ):
        """
        verification code is unique for each student and
        it is stored in their profile.
        """
        student_email: str = add_student_req.student_email
        try:
            activation_code_record: ActivationCode = (
                await ActivationCodeModel().verify_activation_code(
                    student_email=student_email,
                    activation_code=add_student_req.activation_code,
                )
            )

            organization_id: int = activation_code_record.organization_id
            organization: Organization = await self.model.get(organization_id)

            # TODO: implement RAW query to check max member condition.

            await StudentModel().set_activation_attempt(student_email)

            return await StudentModel().join_organization(
                organization_id=organization.id, student_email=student_email
            )
        except IncorrectActivationCodeException:
            await StudentModel().set_activation_attempt(
                student_email=student_email, correct=False
            )
            raise IncorrectActivationCodeException()
