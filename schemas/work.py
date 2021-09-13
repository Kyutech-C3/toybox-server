from typing import Optional
from .community import Community
from .user import User
from pydantic import BaseModel

class PostWork(BaseModel):
    title: str
    description: str
    community_id: str
    github_url: Optional[str]
    work_url: Optional[str]
    private: bool

    class Config:
        orm_mode = True

class Work(BaseModel):
    id: str
    title: str
    description: str
    description_html: str
    github_url: Optional[str]
    work_url: Optional[str]
    user: User
    community: Community
    private: bool

    class Config:
        orm_mode = True
