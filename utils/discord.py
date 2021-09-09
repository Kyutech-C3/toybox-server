import requests
from pydantic import BaseModel
from typing import Optional
import os

API_ENDPOINT = 'https://discord.com/api/v8'
CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')
HOST_URL = os.environ.get('HOST_URL')

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

def discord_exchange_code(code: str) -> DiscordAccessTokenResponse:
  data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': f'{HOST_URL}/api/v1/auth/discord/callback'
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  print(data)

  r = requests.post(f'{API_ENDPOINT}/oauth2/token', data=data, headers=headers)
  print(r.json())
  r.raise_for_status()
  return DiscordAccessTokenResponse(**r.json())

def discord_refresh_token(refresh_token: str) -> DiscordAccessTokenResponse:
  data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'refresh_token',
    'refresh_token': refresh_token
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }

  r = requests.post(f'{API_ENDPOINT}/oauth2/token', data=data, headers=headers)
  r.raise_for_status()
  return DiscordAccessTokenResponse(**r.json())

def discord_fetch_user(access_token: str) -> DiscordUser:
  headers = {
    'Authorization': f'Bearer {access_token}'
  }

  r = requests.get(f'{API_ENDPOINT}/users/@me', headers=headers)
  user = DiscordUser(**r.json())
  return user