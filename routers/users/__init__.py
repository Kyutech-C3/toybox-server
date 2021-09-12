from sqlalchemy.orm.session import Session
from db import get_db
from cruds.users.auth import get_current_user
from fastapi import APIRouter
from fastapi.params import Depends
from schemas.user import User

user_router = APIRouter()

@user_router.get('/@me')
async def get_me(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
  return user