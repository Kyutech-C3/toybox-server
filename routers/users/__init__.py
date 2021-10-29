from sqlalchemy.orm.session import Session
from db import get_db
from cruds.users.auth import GetCurrentUser
from cruds.users import get_user_by_id, get_users, change_user_info
from fastapi import APIRouter
from fastapi.params import Depends
from schemas.user import User, UserInfoChangeRequest

user_router = APIRouter()

@user_router.get('/@me')
async def get_me(db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
  user = get_user_by_id(db, user.id)
  return user

@user_router.get('/{user_id}')
async def get_user(user_id: str, db: Session = Depends(get_db)):
  user = get_user_by_id(db, user_id)
  return user

@user_router.get('')
async def get_user_list(limit: int = 30, offset_id: str = None, db: Session = Depends(get_db)):
  users = get_users(db, limit, offset_id)
  return users

@user_router.put('/@me')
async def put_user_info(payload: UserInfoChangeRequest, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
  user = change_user_info(db, user.id, payload.display_name, payload.profile, payload.avatar_url)
  return user