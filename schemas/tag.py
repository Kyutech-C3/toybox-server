from db.models import Community
from pydantic import BaseModel

class Tag(BaseModel):
    id: str
    name: str
    community: Community
    color: str

    class Config:
        orm_mode = True