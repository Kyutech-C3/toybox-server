from datetime import datetime

from pydantic import BaseModel

from .user import User
from .work import Work


class BaseFavorite(BaseModel):
    work: Work
    user: User
    created_at: datetime

    class Config:
        orm_mode = True


class Favorite(BaseModel):
    favorites: list[BaseFavorite]
    is_favorite: bool
    favorite_count: int
