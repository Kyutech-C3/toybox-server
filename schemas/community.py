from pydantic import BaseModel

class Community(BaseModel):
    id: str
    name: str
    description: str
    description_html: str

    class Config:
        orm_mode = True