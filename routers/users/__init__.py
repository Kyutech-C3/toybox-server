from sqlalchemy.orm.session import Session
from db import get_db
from cruds.users.auth import GetCurrentUser
from fastapi import APIRouter
from fastapi.params import Depends
from schemas.user import User

user_router = APIRouter()

@user_router.get('/@me')
async def get_me(db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
  return user