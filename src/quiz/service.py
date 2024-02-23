from prisma.models import Question

from src.quiz.model import QuestionModel
from src.quiz.serializers import CreateQuestion, EditQuestion


class QuestionService:
    def __init__(self) -> None:
        self.model = QuestionModel()

    async def create_question(self, question_data: CreateQuestion):
        question_data.question = question_data.question.json(exclude_unset=True)
        new_question: Question = await self.model.create(question_data)
        return new_question

    async def get_question(self, question_id: int) -> Question:
        question: Question = await self.model.get(id_=question_id)
        del question.answer_id
        return question

    async def get_questions_by_grade(
        self,
        grade: int,
        skip: int = 0,
        limit: int = 60,
    ) -> list[Question]:
        questions: list[Question] = await self.model.find_many(
            where={"grade": grade},
            include={},
            skip=skip,
            limit=limit,
        )
        return questions

    async def update_question(
        self,
        question_id: int,
        question_edit: EditQuestion,
    ):
        question: Question = await self.get_question(question_id)
        updated_question = await self.model.update(
            question_id,
            question,
            question_edit,
        )
        return updated_question
