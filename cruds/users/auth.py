from db.models import User
from db import get_db
from os import environ
from schemas.user import TokenData
from fastapi.exceptions import HTTPException
from fastapi import Depends, status, Cookie
from cruds.users import get_user
from sqlalchemy.orm.session import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional, Union
from datetime import datetime, timedelta
from utils.discord import (
    DiscordAccessTokenResponse,
    discord_fetch_user,
    discord_verify_user_belongs_to_valid_guild,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

AUTH_COOKIE_KEY = environ.get("AUTH_COOKIE_KEY")

SECRET_KEY = environ.get("TOKEN_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def authenticate_discord_user(
    discord_token: DiscordAccessTokenResponse, db: Session = Depends(get_db)
) -> str:
    discord_user = discord_fetch_user(discord_token.access_token)

    u = db.query(User).filter(User.discord_user_id == discord_user.id).first()

    discord_verify_user_belongs_to_valid_guild(access_token=discord_token.access_token)

    if u == None:
        # user's first login
        u = User(
            name=discord_user.username,
            email=discord_user.email,
            display_name=discord_user.username,
            discord_token=discord_token.access_token,
            discord_refresh_token=discord_token.refresh_token,
            discord_user_id=discord_user.id,
            avatar_url="https://cdn.discordapp.com/avatars/{user_id}/{avatar_id}.png".format(
                user_id=discord_user.id, avatar_id=discord_user.avatar
            ),
        )
        db.add(u)
        db.commit()
    else:
        u.avatar_url = (
            "https://cdn.discordapp.com/avatars/{user_id}/{avatar_id}.png".format(
                user_id=discord_user.id, avatar_id=discord_user.avatar
            )
        )
        db.commit()

    token = create_access_token(u)
    return token


def create_access_token(
    user: User, expires_delta: Optional[timedelta] = timedelta(minutes=15)
) -> str:
    to_encode = {"sub": user.email, "token_type": "bearer"}
    expire = datetime.utcnow() + expires_delta
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class GetCurrentUser:
    def __init__(self, auto_error: bool = True) -> None:
        self.auto_error = auto_error

    def __call__(
        self,
        db: Session = Depends(get_db),
        token: Union[str, None] = Cookie(default=None, alias=AUTH_COOKIE_KEY),
    ):
        try:
            if token == None:
                return self.handle_error(detail="Credential is missing")

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return self.handle_error(detail="Email is missing")
            token_data = TokenData(email=email)
            print("token", token_data)
        except JWTError:
            return self.handle_error(detail="JWT error")
        user = get_user(db, token_data.email)
        if user is None:
            return self.handle_error(detail="User not found")
        return user

    def handle_error(self, detail: str = "Authorization error"):
        if self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=detail,
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            return None
