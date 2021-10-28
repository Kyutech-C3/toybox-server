from pydantic import BaseModel, EmailStr, HttpUrl
from datetime import datetime
from typing import Optional

class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    display_name: str
    avatar_url: Optional[HttpUrl]

class UserInfoChangeRequest(BaseModel):
    display_name: Optional[str]
    avatar_url: Optional[HttpUrl]
    profile: Optional[str]

class User(BaseModel):
    id: str
    name: str
    email: str
    display_name: str
    avatar_url: Optional[HttpUrl]
    profile: Optional[str]
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