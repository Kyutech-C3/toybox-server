from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import validator

from db import Visibility
from schemas.tag import GetTag
from schemas.user import User

from .asset import BlogAsset


class PostBlog(BaseModel):
    title: str
    body_text: str
    visibility: str
    thumbnail_asset_id: str
    assets_id: list[str]
    tags_id: list[str]
    published_at: Optional[datetime]

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
    assets: list[BlogAsset]
    visibility: str
    tags: list[GetTag]
    thumbnail: BlogAsset
    favorite_count: Optional[int]
    is_favorite: Optional[bool]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]

    class Config:
        orm_mode = True


class BlogsResponse(BaseModel):
    blogs: list[Blog]
    blogs_total_count: int
