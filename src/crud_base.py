from typing import Any, Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from src.exceptions import (
    DBCreateException,
    DBDeleteException,
    DBUpdateException,
    EmailNotFoundException,
    NoSuchRecordException,
    PhoneNumberNotFoundException,
    QueryException,
    RecordNotFoundException,
    UniqueConstraintFailedException,
)

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBaseModel(Generic[CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A Prisma Client model class
        """
        self.model = model

    @staticmethod
    def get_update_data(new_data):
        """
        Get new data to update as a dict for easy access.
        """
        if isinstance(new_data, dict):
            return new_data

        update_data = new_data.dict(exclude_unset=True)
        return update_data

    @staticmethod
    def update_old_data(old_data, old_data_obj, update_data):
        """Update the old data obj and convert into a dict for easy access.

        Parameters:
        old_data (dict): data in DB as a dict.
        old_data_obj (db_obj): DB object representing data in DB.
        update_data (dict): data to update old_data_obj with.

        Returns:
            dict:updated data as a dict.
        """

        for field in old_data:
            if field in update_data:
                setattr(old_data_obj, field, update_data[field])
        return old_data_obj.dict(exclude_none=True)

    async def get(self, id_: Any, include=None):
        if include is not None:
            record = await self.model.prisma().find_unique(
                where={"id": id_}, include=include
            )
        else:
            record = await self.model.prisma().find_unique(
                where={"id": id_}, include=include
            )

        if not record:
            raise RecordNotFoundException(id_)
        return record

    async def find_many(self, where, include, skip=0, limit=100):
        record = await self.model.prisma().find_many(
            where=where, include=include, skip=skip, take=limit
        )
        return record

    async def get_groups(self, group_by: list[str], where: dict[str, any]):
        record = await self.model.prisma().group_by(by=group_by, where=where)
        if not record:
            raise NoSuchRecordException("record group not found")
        return record

    async def get_unique(self, where, include=None):
        if not include:
            include = {}
        record = await self.model.prisma().find_unique(where=where, include=include)
        if not record:
            raise NoSuchRecordException("No such unique record found")
        return record

    async def get_first(self, where, include):
        record = await self.model.prisma().find_first(where=where, include=include)
        return record

    async def get_by_email(self, email: str):
        record = await self.model.prisma().find_unique(where={"email": email})
        if not record:
            raise EmailNotFoundException(email)
        return record

    async def get_by_phone_number(self, phone_number: str):
        record = await self.model.prisma().find_unique(
            where={"phone_number": phone_number}
        )
        if not record:
            raise PhoneNumberNotFoundException(phone_number)
        return record

    async def get_all(self, skip: int = 0, limit: int = 100):
        try:
            records = await self.model.prisma().find_many(skip=skip, take=limit)
            return records

        except Exception as e:
            raise QueryException(e)

    async def conditional_get_all(self, _id: int, query_field: str):
        try:
            records = await self.model.prisma().find_many(where={query_field: _id})
            return records

        except Exception as e:
            raise QueryException(e)

    async def create(self, obj_in: CreateSchemaType):
        try:
            obj_in_data = jsonable_encoder(obj_in, exclude_unset=True)
            result = await self.model.prisma().create(data=obj_in_data)
            return result

        except Exception as e:
            if str(e).startswith("Unique constraint failed"):
                raise UniqueConstraintFailedException(str(e))

            raise DBCreateException(e)

    async def create_many(
        self,
        obj_in: list[CreateSchemaType],
        skip_duplicates=True,
    ):
        try:
            obj_in_data = jsonable_encoder(obj_in)
            result = await self.model.prisma().create_many(
                data=obj_in_data, skip_duplicates=skip_duplicates
            )
            return result
        except Exception as e:
            raise DBCreateException(e)

    async def update(self, _id: int, old_data, new_data: UpdateSchemaType):
        update_data = CRUDBaseModel.get_update_data(new_data)
        updated_data = CRUDBaseModel.update_old_data(
            old_data.dict(exclude_none=False), old_data, update_data
        )

        try:
            result = await self.model.prisma().update(
                where={"id": _id}, data=updated_data
            )
            return result
        except Exception as e:
            raise DBUpdateException(e)

    async def update_by_email(self, email: str, old_data, new_data: UpdateSchemaType):
        update_data = CRUDBaseModel.get_update_data(new_data)
        updated_data = CRUDBaseModel.update_old_data(
            old_data.dict(exclude_none=True), old_data, update_data
        )

        try:
            result = await self.model.prisma().update(
                where={"email": email}, data=updated_data
            )
            return result
        except Exception as e:
            raise DBUpdateException(e)

    async def update_field(self, where: dict, data: dict):
        try:
            result = await self.model.prisma().update(where=where, data=data)
            return result
        except Exception as e:
            raise DBUpdateException(e)

    async def remove(self, id_: int):
        """removes the object which is returned when queried by its `id`

        Args:
            id_ (int): id of the object in the DB table

        Raises:
            HTTPException: in-case of DB level errors or network faults

        Returns:
            _type_: JSON object with `status` and `message`
        """
        try:
            await self.model.prisma().delete(where={"id": id_})
            deleted = {
                "status": "Success",
                "message": f"Resource with id : {id_} deleted",
            }
            return deleted

        except Exception as e:
            raise DBDeleteException(e)

    async def remove_by_email(self, email: str):
        try:
            await self.model.prisma().delete(where={"email": email})
            deleted = {
                "status": "Success",
                "message": f"Resource with email : {email} deleted",
            }
            return deleted

        except Exception as e:
            raise DBDeleteException(e)
