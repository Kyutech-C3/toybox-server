from typing import Optional
from db.models import User, Work
from pydantic import BaseModel
from pydantic.errors import StrRegexError

class Asset(BaseModel):
    id: str
    work: Work
    asset_type: str
    thumb_url: Optional[str]
    url: Optional[str]
    user: User

    class Config:
        orm_mode = True