from .community import Community
from pydantic import BaseModel

class BaseTag(BaseModel):
    name: str
    community_id: str
    color: str
class Tag(BaseTag):
    id: str
    name: str
    community: Community
    color: str
    class Config:
        orm_mode = True