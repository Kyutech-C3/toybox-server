import os
from starlette.responses import Response, RedirectResponse
from cruds.users.auth import authenticate_discord_user
from fastapi.params import Depends
from db import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from utils.discord import discord_exchange_code

FRONTEND_HOST_URL = os.environ.get("FRONTEND_HOST_URL")
CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
HOST_URL = os.environ.get("HOST_URL")
AUTH_COOKIE_KEY = os.environ.get("AUTH_COOKIE_KEY")

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@auth_router.get("/discord")
async def discord_login_redirect():
    redirect_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={HOST_URL}/api/v1/auth/discord/callback&response_type=code&scope=identify email guilds"
    return RedirectResponse(url=redirect_url)


@auth_router.get("/discord/callback")
async def discord_callback(code: str = "", db: Session = Depends(get_db)):
    r = discord_exchange_code(code)
    token = authenticate_discord_user(r, db)
    res = RedirectResponse(
        FRONTEND_HOST_URL,
    )
    res.set_cookie(AUTH_COOKIE_KEY, token, httponly=True, samesite="strict")
    return res


@auth_router.post("/logout")
async def logout():
    response = Response()
    response.set_cookie(AUTH_COOKIE_KEY, "")
    return response
