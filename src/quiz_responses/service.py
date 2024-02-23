from prisma.models import QuizResponse

from src.quiz_responses.model import QuizResponseModel
from src.quiz_responses.serializers import CreateQuizResponse, EditQuizResponse


class QuizResponseService:
    def __init__(self) -> None:
        self.model = QuizResponseModel()

    async def create_response(self, data: CreateQuizResponse):
        data.response = data.response.json(exclude_unset=True)
        new_response: QuizResponse = await self.model.create(data)
        return new_response

    async def get_response(self, response_id: int) -> QuizResponse:
        response: QuizResponse = await self.model.get(id_=response_id)
        return response

    async def update_response(
        self,
        response_id: int,
        response_edit: EditQuizResponse,
    ):
        response: QuizResponse = await self.get_response(response_id)
        updated_response = await self.model.update(
            response_id,
            response,
            response_edit,
        )
        return updated_response
