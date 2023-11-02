from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from pydantic.class_validators import validator

from db import Visibility
from schemas.tag import GetTag
from schemas.url_info import BaseUrlInfo, UrlInfo

from .asset import Asset
from .user import User


class PostWork(BaseModel):
    title: str
    description: str
    visibility: str
    thumbnail_asset_id: str
    assets_id: List[str]
    urls: List[BaseUrlInfo]
    tags_id: List[str]

    @validator("visibility")
    def value_of(cls, v):
        for e in Visibility:
            if e.value == v:
                return e
        raise ValueError("{} is invalid visibility type.".format(v))


class Work(BaseModel):
    id: str
    title: str
    description: str
    description_html: str
    user: User
    assets: List[Asset]
    urls: List[UrlInfo]
    visibility: str
    tags: List[GetTag]
    thumbnail: Asset
    favorite_count: Optional[int]
    is_favorite: Optional[bool]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ResWorks(BaseModel):
    works: list[Work]
    works_total_count: int
