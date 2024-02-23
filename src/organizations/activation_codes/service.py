from prisma.models import ActivationCode
from src.organizations.activation_codes.utils import generate_otp
from src.organizations.activation_codes.model import ActivationCodeModel
from src.organizations.activation_codes.serializers import (
    CreateActivationCode,
    EditActivationCode,
)


class ActivationCodeService:
    def __init__(self) -> None:
        self.model = ActivationCodeModel()

    async def create(self, activation_code: CreateActivationCode):
        activation_code_value: str = generate_otp()
        activation_code = CreateActivationCode(
            **activation_code.dict(exclude_unset=True),
            activation_code=activation_code_value
        )

        new_activation_code: ActivationCode = await self.model.create(activation_code)

        code: str = activation_code.activation_code
        del new_activation_code.activation_code

        return code, new_activation_code

    async def get(self, activation_code_id: int):
        activation_code: ActivationCode = await self.model.get(activation_code_id)
        return activation_code

    async def get_all(self, skip: int = 0, limit: int = 10):
        activation_codes: list[ActivationCode] = await self.model.get_all(skip, limit)
        return activation_codes

    async def get_activation_code_by_email(self, student_email: str):
        activation_code: ActivationCode = await self.model.get_by_email(student_email)
        return activation_code

    async def update_activation_code(
        self, activation_code_id: int, edit_activation_code_req: EditActivationCode
    ):
        activation_code: ActivationCode = await self.get(activation_code_id)
        updated_activation_code: ActivationCode = await self.model.update(
            activation_code_id, activation_code, edit_activation_code_req
        )
        return updated_activation_code
