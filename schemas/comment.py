from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from pydantic.fields import Field


from cruds import works
from .user import User

class PostComment(BaseModel):
    content: str=Field(..., title="投稿内容", min_length=1, max_length=500)

class ResponseComment(PostComment):
    id: str
    user: Optional[User]
    work_id: str
    scope: Optional[str]
    number_of_reply: int
    reply_at: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
