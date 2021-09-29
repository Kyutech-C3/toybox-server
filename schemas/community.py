from pydantic import BaseModel
from datetime import datetime

class BaseCommunity(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True

class Community(BaseCommunity):
    id: str
    description_html: str
    created_at: datetime
    updated_at: datetime
