from prisma.models import Question

from src.crud_base import CRUDBaseModel
from src.quiz.serializers import CreateQuestion, EditQuestion


class QuestionModel(CRUDBaseModel[CreateQuestion, EditQuestion]):
    def __init__(self):
        super().__init__(Question)
