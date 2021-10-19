from typing import Optional
from .community import Community
from pydantic import BaseModel, ValidationError, validator
import re

class BaseTag(BaseModel):
    name: str
    color: str

    @validator('color')
    def color_code_must_match_format(cls, v):
        if not re.match('#[0-9A-F]{6}', v):
            raise ValueError('not match format')
        return v

class PostTag(BaseTag):
    community_id: str

    class Config:
        orm_mode = True

class PutTag(PostTag):
    name: Optional[str]
    color: Optional[str]
    community_id: Optional[str]

class GetTag(BaseTag):
    id: str
    community: Community

    class Config:
        orm_mode = True

class TagResponsStatus(BaseModel):
    status: str
