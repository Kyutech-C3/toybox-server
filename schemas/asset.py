from pydantic import BaseModel

class Asset(BaseModel):
    room_id: str
    user_id: str
    is_win: bool
    stage: int
    hand: int

    class Config:
        orm_mode = True