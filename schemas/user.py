from time import time
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

class Token(BaseModel):
    refresh_token: str 
    user: User
    expired_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
    
    def has_expired(self):
        return self.expired_at < datetime.now()

class UserWithPlainPassword(User):
    password: str

class RefreshTokenExchangeRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    expired_at: str
    refresh_token: str
    access_token: str

class TokenData(BaseModel):
    email: Optional[str] = None