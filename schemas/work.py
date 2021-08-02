from typing import Optional
from db.models import Community, User
from pydantic import BaseModel

class Work(BaseModel):
    id: str
    title: str
    description: str
    description_html: str
    user: User
    github_url: Optional[str]
    work_url: Optional[str]
    community: Community

    class Config:
        orm_mode = True