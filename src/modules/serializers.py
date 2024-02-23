from typing import Optional

from pydantic import BaseModel


class ModuleDescription(BaseModel):
    title: str


class CreateModule(BaseModel):
    module_number: int
    description: ModuleDescription


class EditModule(BaseModel):
    module_number: Optional[int]
    description: Optional[ModuleDescription]
