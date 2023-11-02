import os

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from cruds.users import (
    authenticate_discord_user,
    create_user,
    get_password_hash,
    get_user,
    renew_token,
)
from db import get_db, models
from schemas.user import (
    RefreshTokenExchangeRequest,
    TokenResponse,
    User,
    UserCreateRequest,
)
from utils.discord import discord_exchange_code

FRONTEND_HOST_URL = os.environ.get("FRONTEND_HOST_URL")
CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
HOST_URL = os.environ.get("HOST_URL")

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@auth_router.post("/sign_up", response_model=User)
def sign_up(user_request: UserCreateRequest, db: Session = Depends(get_db)):
    existing_user = get_user(db, user_request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User has already exists")

    hashed_password = get_password_hash(user_request.password)
    user = models.User(
        name=user_request.name,
        email=user_request.email,
        password_hash=hashed_password,
        display_name=user_request.display_name,
        avatar_url=user_request.avatar_url,
    )

    created_user = create_user(db, user)

    if not created_user:
        raise HTTPException(status_code=500, detail="Couldn't create user")

    return User.from_orm(created_user)


@auth_router.post("/token", response_model=TokenResponse)
async def refresh_token_exchange(
    token_request: RefreshTokenExchangeRequest, db: Session = Depends(get_db)
):
    token = renew_token(token_request.refresh_token, db)
    return token


@auth_router.get("/discord")
async def discord_login_redirect():
    redirect_url = (
        "https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}&redirect_uri={HOST_URL}/api/v1/auth/discord/callback"
        "&response_type=code&scope=identify email guilds"
    )
    return RedirectResponse(url=redirect_url)


@auth_router.get("/discord/callback", response_model=TokenResponse)
async def discord_callback(code: str = "", db: Session = Depends(get_db)):
    r = discord_exchange_code(code)
    token_response = authenticate_discord_user(r, db)
    return RedirectResponse(
        f"{FRONTEND_HOST_URL}/discord?access_token={token_response.access_token}"
        f"&refresh_token={token_response.refresh_token}"
        f"&expired_at={token_response.expired_at}"
    )
