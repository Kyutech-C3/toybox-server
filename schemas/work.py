from datetime import datetime
from typing import List, Optional
from pydantic.class_validators import validator
from db.models import Visibillity
from schemas.url_info import BaseUrlInfo, UrlInfo
from .community import Community
from .user import User
from .asset import Asset
from pydantic import BaseModel

class PostWork(BaseModel):
    title: str
    description: str
    community_id: str
    visibillity: str
    thumbnail_asset_id: Optional[str]
    assets_id: List[str]
    urls: List[BaseUrlInfo]

    @validator('visibillity')
    def value_of(cls, v):
        for e in Visibillity:
            if e.value == v:
                return e
        raise ValueError('{} is invalid visibillity type.'.format(v))

class Work(BaseModel):
    id: str
    title: str
    description: str
    description_html: str
    user: User
    community: Community
    assets: List[Asset]
    urls: List[UrlInfo]
    visibillity: str
    thumbnail: Optional[Asset]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
