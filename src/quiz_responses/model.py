from prisma.models import QuizResponse

from src.crud_base import CRUDBaseModel
from src.quiz_responses.serializers import CreateQuizResponse, EditQuizResponse


class QuizResponseModel(CRUDBaseModel[CreateQuizResponse, EditQuizResponse]):
    def __init__(self):
        super().__init__(QuizResponse)
