from pydantic import BaseModel

class User(BaseModel):
    id: str
    name: str
    room_id: str

    class Config:
        orm_mode = True
