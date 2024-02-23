from prisma.models import ActivationCode
from pydantic import SecretStr

from src.auth.exceptions import IncorrectActivationCodeException
from src.crud_base import CRUDBaseModel
from src.organizations.activation_codes.serializers import (
    CreateActivationCode,
    EditActivationCode,
)


class ActivationCodeModel(CRUDBaseModel[CreateActivationCode, EditActivationCode]):
    def __init__(self):
        super().__init__(ActivationCode)

    async def verify_activation_code(
        self, student_email: str, activation_code: SecretStr
    ) -> ActivationCode:
        """
        Verify the activation code by matching it with the provided email.
        Caller must ensure the user owns the email provided, the method does
        implement any checks for that.
        :param student_email: Email of the user that owns the activation code.
        :param activation_code: Random 6 character activation code string.
        :return: ActivationCode
        """
        activation_code_record: ActivationCode = await super().get_unique(
            where={"student_email": student_email}
        )

        if activation_code_record.activation_code != activation_code.get_secret_value():
            raise IncorrectActivationCodeException

        return activation_code_record
