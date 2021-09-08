from pydantic import BaseModel, validator, EmailStr, HttpUrl
from datetime import date, datetime
from typing import Optional

class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    display_name: str
    avatar_url: Optional[HttpUrl]


class User(BaseModel):
    id: str
    name: str
    email: str
    display_name: str
    discord_token: Optional[str]
    discord_refresh_token: Optional[str]
    discord_user_id: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserWithPlainPassword(User):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None