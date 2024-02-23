from pydantic import BaseModel, Field

from src.db.model import PyObjectId, RWModel
from src.learn.model import SectionModel


class TopicModel(BaseModel):
    """
    Number of topics in a module are ordered and limited.
    The `id` field is an integer representing the `nth` topic.
    Where `n > 0`.
    """

    id: int
    title: str


class ModuleModel(RWModel):
    """
    A module is a reference for the LLM to generate relevant content.
    It is also required for tracking user progress.
    """

    topics: list[TopicModel]
    module_number: int
    module_name: str


class LessonModel(RWModel):
    """
    A lesson is created by the LLM for a module topic.
    There can be multiple lessons for a single topic.
    """

    user_id: int
    module_id: PyObjectId = Field(default_factory=PyObjectId)
    topic_id: int
    sections: list[SectionModel]
    finished: bool = Field(default=False)


class LessonModelRequest(BaseModel):
    sections: list[SectionModel]
    module_id: str
