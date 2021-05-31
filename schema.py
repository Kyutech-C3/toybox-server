from pydantic import BaseModel
from typing import Optional, List

class User(BaseModel):
    id: str
    name: str
    room_id: str

    class Config:
        orm_mode = True

class Room(BaseModel):
    id: str
    name: str
    latest_stage: str
    host_user: User

    class Config:
        orm_mode = True

class Result(BaseModel):
    room_id: str
    user_id: str
    is_win: bool
    stage: int
    hand: int

class CreateRoomRequest(BaseModel):
    user_name: str
    room_name: str

class CreateRoomResponse(BaseModel):
    room: Room
    user: User

class JoinRoomRequest(BaseModel):
    user_name: str

class JoinRoomResponse(CreateRoomResponse):
    pass

class StartGameRequest(BaseModel):
    user_id: str

class NewHandData(BaseModel):
    user_id: str
    room_id: str
    hand: int

class PostResult(NewHandData):
    pass

class NewUserResponse(BaseModel):
    id: str
    name: str
    room_id: str

class GameResultData(BaseModel):
    data: List[Result]