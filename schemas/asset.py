from typing import Optional
from .user import User
from .work import Work
from pydantic import BaseModel

class Asset(BaseModel):
    id: str
    work: Work
    asset_type: str
    thumb_url: Optional[str]
    url: Optional[str]
    user: User

    class Config:
        orm_mode = True