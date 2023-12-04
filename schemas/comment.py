from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.fields import Field

from .user import User


class PostComment(BaseModel):
    content: str = Field(..., title="投稿内容", min_length=1, max_length=500)


class ResponseReplyComment(PostComment):
    id: str
    user: Optional[User]
    work_id: str
    visibility: Optional[str]
    reply_at: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ResponseComment(ResponseReplyComment):
    id: str
    user: Optional[User]
    work_id: str
    visibility: Optional[str]
    number_of_reply: int
    reply_at: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
