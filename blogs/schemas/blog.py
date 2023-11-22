from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import validator

from db import Visibility
from schemas.tag import GetTag
from schemas.user import User

from .asset import Asset


class PostBlog(BaseModel):
    title: str
    body_text: str
    visibility: str
    thumbnail_asset_id: str
    assets_id: list[str]
    tags_id: list[str]

    @validator("visibility")
    def value_of(cls, v):
        for e in Visibility:
            if e.value == v:
                return e
        raise ValueError("{} is invalid visibility type.".format(v))


class Blog(BaseModel):
    id: str
    title: str
    body_text: str
    user: User
    assets: list[Asset]
    visibility: str
    tags: list[GetTag]
    thumbnail: Asset
    favorite_count: Optional[int]
    is_favorite: Optional[bool]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class BlogsResponse(BaseModel):
    blogs: list[Blog]
    blogs_total_count: int
