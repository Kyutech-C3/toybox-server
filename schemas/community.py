from pydantic import BaseModel

class BaseCommunity(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True

class Community(BaseCommunity):
    id: str
    description_html: str
