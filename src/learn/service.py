import json

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from src.learn.serializers import LessonModel, ModuleModel, SectionModel, TopicModel
from src.learn.utils import EVOLVE_LEARNING, LESSONS, MODULES
from src.openai.service import OpenAIService


class LearnService:
    def __init__(self, db: AsyncIOMotorClient) -> None:
        # reference to the learn database.
        self.db = db[EVOLVE_LEARNING]
        # number of lessons that a `find` query should buffer in a list.
        self.max_lessons = 10

    async def get_current_lesson(self, user_id: int):
        """Get the last ongoing lesson, if any or create a new one."""
        ongoing_lessons: list[LessonModel] = (
            await self.db[LESSONS]
            .find(
                filter={
                    "finished": False,
                    "user_id": user_id,
                },
                sort=[("created_at", -1)],
            )
            .to_list(self.max_lessons)
        )

        if ongoing_lessons and len(ongoing_lessons) > 0:
            return ongoing_lessons[0]

        print("no ongoing lessons, creating new lesson....")
        ongoing_lessons = await self.create_lesson(user_id=user_id)
        return ongoing_lessons

    async def create_lesson(
        self,
        user_id: int,
    ) -> LessonModel:
        last_lesson: list[LessonModel] = (
            await self.db[LESSONS]
            .find(
                filter={"user_id": user_id},
                sort=[("created_at", -1)],
            )
            .to_list(1)
        )

        if last_lesson and len(last_lesson) > 0:
            last_lesson: LessonModel = LessonModel(**last_lesson[0])
        else:
            first_module: ModuleModel = ModuleModel(
                **(
                    await self.db[MODULES].find_one(
                        {"module_number": 1},
                    )
                )
            )
            # create a first topic if one does not exist.
            first_topic: TopicModel | None = None
            if len(first_module.topics) == 0:
                first_topic = TopicModel(id=1, title=first_module.module_name)
            else:
                first_topic: dict | TopicModel = first_module.topics[0]
                first_topic: TopicModel = (
                    TopicModel(**first_topic)
                    if isinstance(first_topic, dict)
                    else TopicModel(**first_topic.dict())
                )

            sections: list[SectionModel] = self._create_lesson_gpt(
                topic=first_topic,
                module=first_module,
            )

            lesson_model = LessonModel(
                user_id=user_id,
                sections=sections,
                topic_id=first_topic.id,
                module_id=first_module.id,
            )

            lesson = jsonable_encoder(lesson_model)
            new_lesson = await self.db[LESSONS].insert_one(lesson)
            created_lesson: LessonModel = await self.db[LESSONS].find_one(
                {"_id": new_lesson.inserted_id}
            )
            return created_lesson

        if not last_lesson.finished:
            return last_lesson

        """
        Module:
            Topic:
                Lesson

        Generate the next lesson
        """
        print("Last Lesson", last_lesson.module_id)
        current_module: dict = await self.db[MODULES].find_one(
            {"_id": str(last_lesson.module_id)},
        )

        current_module = ModuleModel(**current_module)

        next_topic_id: int = last_lesson.topic_id + 1
        next_module: ModuleModel = current_module
        if next_topic_id > len(current_module.topics):
            print(
                f"INFO: module {current_module.module_number} topics finished, moving to next module"
            )
            # no more topics are left in the current module
            # move to the next module.
            next_module_number = current_module.module_number + 1
            next_module = await self.db[MODULES].find_one(
                {"module_number": next_module_number}
            )
            # reset topic id to the first topic of the next module
            next_topic_id = 1
            if not next_module:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"All modules finished. Last Module: {next_module_number - 1}",
                )
            next_module = ModuleModel(**next_module)

        """safest way to avoid index erros is to scan the list and match
        the expected topic id.
        """
        next_topic: TopicModel | None = None
        for topic in next_module.topics:
            if topic.id == next_topic_id:
                next_topic = topic
        print("Next Topic", next_topic.title)
        print("Next Module", next_module.module_number)
        # handle case: no topic.
        if not next_topic:
            next_topic = TopicModel(id=1, title=next_module.module_name)

        print("calling Gippity....")
        gpt_content: list[SectionModel] = self._create_lesson_gpt(
            topic=next_topic,
            module=next_module,
        )
        print("Gippity done")
        lesson_model = LessonModel(
            user_id=user_id,
            sections=gpt_content,
            topic_id=next_topic.id,
            module_id=next_module.id,
        )

        lesson = jsonable_encoder(lesson_model)
        new_lesson = await self.db[LESSONS].insert_one(lesson)
        created_lesson: LessonModel = await self.db[LESSONS].find_one(
            {"_id": new_lesson.inserted_id}
        )
        return created_lesson

    async def create_new_module(self, req: ModuleModel) -> ModuleModel:
        module = jsonable_encoder(req)
        new_module = await self.db[MODULES].insert_one(module)
        created_module: ModuleModel = await self.db[MODULES].find_one(
            {"_id": new_module.inserted_id}
        )
        return created_module

    async def finish_lesson(self, user_id: int) -> str | None:
        """Get the last ongoing lesson, if any or create a new one."""
        ongoing_lessons: list[LessonModel] = (
            await self.db[LESSONS]
            .find(
                filter={
                    "finished": False,
                    "user_id": user_id,
                },
                sort=[("created_at", -1)],
            )
            .to_list(self.max_lessons)
        )

        if not ongoing_lessons or len(ongoing_lessons) == 0:
            return None

        await self.db[LESSONS].update_one(
            {"_id": ongoing_lessons[0]["_id"]},
            {"$set": {"finished": True}},
        )
        return ongoing_lessons[0]["_id"]

    def _create_lesson_gpt(
        self, topic: TopicModel, module: ModuleModel
    ) -> list[SectionModel]:
        """Create a lesson using GPT-3 and parse its output."""
        new_lesson_content = OpenAIService().create_new_lesson(
            topic=topic,
            module=module,
        )
        content: dict = json.loads(new_lesson_content)

        sections: list[SectionModel] = []
        for section in content["sections"]:
            sections.append(SectionModel(**section))

        return sections
