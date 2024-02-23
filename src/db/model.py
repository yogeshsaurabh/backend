from datetime import datetime, timezone
from typing import Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


def datetime_now() -> datetime:
    return datetime.now(tz=timezone.utc)


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime] = Field(default_factory=datetime_now)
    updated_at: Optional[datetime] = Field(default_factory=datetime_now)


class DBModelMixin(DateTimeModelMixin):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")


class RWModel(DBModelMixin):
    class Config:
        allow_population_by_field_name = (True,)
        arbitrary_types_allowed = (True,)
        json_encoders = {
            datetime: lambda dt: dt.replace(tzinfo=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            ObjectId: str,
        }
