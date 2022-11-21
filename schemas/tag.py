from typing import Optional
from pydantic import BaseModel, ValidationError, validator
import re


class BaseTag(BaseModel):
    name: str
    color: str

    @validator("color")
    def color_code_must_match_format(cls, v):
        if not re.match("#[0-9a-fA-F]{6}$", v):
            raise ValueError("not match format")
        return v


class PostTag(BaseTag):
    class Config:
        orm_mode = True


class PutTag(PostTag):
    name: Optional[str]
    color: Optional[str]


class GetTag(BaseTag):
    id: str

    class Config:
        orm_mode = True


class TagResponsStatus(BaseModel):
    status: str
