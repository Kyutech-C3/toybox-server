from datetime import datetime
from typing import List, Optional
from pydantic.class_validators import validator
from db.models import Visibility
from schemas.tag import GetTag
from schemas.url_info import BaseUrlInfo, UrlInfo
from .user import User
from .asset import Asset
from pydantic import BaseModel

class PostWork(BaseModel):
    title: str
    description: str
    visibility: str
    thumbnail_asset_id: Optional[str]
    assets_id: List[str]
    urls: List[BaseUrlInfo]
    tags_id: List[str]

    @validator('visibility')
    def value_of(cls, v):
        for e in Visibility:
            if e.value == v:
                return e
        raise ValueError('{} is invalid visibility type.'.format(v))

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
    thumbnail: Optional[Asset]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SearchOption(BaseModel):
    tags: list[str]
