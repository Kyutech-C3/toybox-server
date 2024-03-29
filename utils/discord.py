import json
import os
import urllib.error
import urllib.request
from typing import List, Optional

import requests
from fastapi import HTTPException
from pydantic import BaseModel

API_ENDPOINT = "https://discord.com/api/v8"
CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
HOST_URL = os.environ.get("HOST_URL")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")


class DiscordAccessTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str


class DiscordUser(BaseModel):
    id: str
    username: str
    discriminator: str
    avatar: Optional[str]
    bot: Optional[bool]
    system: Optional[bool]
    mfa_enabled: Optional[bool]
    banner: Optional[str]
    accent_color: Optional[int]
    locale: Optional[str]
    verified: Optional[bool]
    email: Optional[str]
    flags: Optional[int]
    premium_type: Optional[int]
    public_flags: Optional[int]


class DiscordGuild(BaseModel):
    id: str
    name: str
    icon: Optional[str]
    owner: bool
    permissions: Optional[str]


class DiscordException(HTTPException):
    def __init__(
        self,
        discord_status_code: int,
        status_code: int = 500,
        detail: str = "An error occured",
    ):
        super().__init__(
            status_code=status_code, detail=f"[Discord: {discord_status_code}] {detail}"
        )


def discord_exchange_code(code: str) -> DiscordAccessTokenResponse:
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"{HOST_URL}/api/v1/auth/discord/callback",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    r = requests.post(f"{API_ENDPOINT}/oauth2/token", data=data, headers=headers)

    if r.status_code != 200:
        raise DiscordException(
            discord_status_code=r.status_code, detail="Requesting token has failed"
        )

    return DiscordAccessTokenResponse(**r.json())


def discord_refresh_token(refresh_token: str) -> DiscordAccessTokenResponse:
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    r = requests.post(f"{API_ENDPOINT}/oauth2/token", data=data, headers=headers)

    if r.status_code != 200:
        raise DiscordException(
            discord_status_code=r.status_code,
            detail="Request for token refreshing has failed",
        )

    return DiscordAccessTokenResponse(**r.json())


def discord_fetch_user(access_token: str) -> DiscordUser:
    headers = {"Authorization": f"Bearer {access_token}"}

    r = requests.get(f"{API_ENDPOINT}/users/@me", headers=headers)
    if r.status_code != 200:
        raise DiscordException(
            discord_status_code=r.status_code, detail="Request to /users/@me failed"
        )
    user = DiscordUser(**r.json())
    return user


def discord_fetch_user_guilds(access_token: str) -> List[DiscordGuild]:
    headers = {"Authorization": f"Bearer {access_token}"}

    r = requests.get(f"{API_ENDPOINT}/users/@me/guilds", headers=headers)
    if r.status_code != 200:
        raise DiscordException(
            discord_status_code=r.status_code,
            detail="Request to /users/@me/guilds failed",
        )
    guilds: List[DiscordGuild] = []
    for _guild in r.json():
        guilds.append(DiscordGuild(**_guild))

    return guilds


def discord_verify_user_belongs_to_valid_guild(access_token: str) -> bool:
    guilds = discord_fetch_user_guilds(access_token=access_token)
    valid_guild_ids = os.environ.get("DISCORD_GUILD_ID").split(",")

    for guild in guilds:
        for valid_guild_id in valid_guild_ids:
            if guild.id == valid_guild_id:
                return True

    raise DiscordException(
        discord_status_code=403, detail="User not belongs to valid guild"
    )


def notice_discord(
    user_name: str,
    user_icon_url: str,
    work_title: str,
    work_description: str,
    work_url: str,
    thumbnail_image_url: str,
):
    desc = work_description
    if len(work_description) > 100:
        desc = work_description[:100] + "…"

    main_content = {
        "username": user_name,
        "avatar_url": user_icon_url,
        "embeds": [
            {
                "title": work_title,
                "url": work_url,
                "description": desc,
                "thumbnail": {
                    "url": (
                        "https://toybox.compositecomputer.club"
                        "/_nuxt/img/ToyBoxlogo.21166b5.png"
                    )
                },
                "color": 4063189,
                "image": {"url": thumbnail_image_url},
            }
        ],
    }
    res = requests.post(
        DISCORD_WEBHOOK_URL,
        json.dumps(main_content),
        headers={"Content-Type": "application/json"},
    )

    try:
        res.raise_for_status()
    except Exception as e:
        print(e)


def download_discord_avatar(discord_user_id, avatar_id) -> bin:
    try:
        req = urllib.request.Request(
            f"https://cdn.discordapp.com/avatars/{discord_user_id}/{avatar_id}.png"
        )
        req.add_header("User-Agent", "Mozilla/5.0")
        file = urllib.request.urlopen(req)
        return file.read()
    except urllib.error.URLError as e:
        print(e)
