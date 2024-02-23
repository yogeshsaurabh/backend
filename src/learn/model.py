from enum import Enum

from pydantic import BaseModel


class ContentType(str, Enum):
    HEADING = "HEADING"
    PARAGRAPH = "PARAGRAPH"
    ORDERED_LIST = "ORDERED_LIST"
    UNORDERED_LIST = "UNORDERED_LIST"


class ContentBlockModel(BaseModel):
    type: ContentType
    text: str | None
    items: list[str] | None


class SectionModel(BaseModel):
    """A section is a part of an AI generated lesson `Lesson`."""

    # ID is just for ordering of sections.
    id: int
    content: list[ContentBlockModel]
