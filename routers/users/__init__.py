from sqlalchemy.orm.session import Session
from db import get_db
from cruds.users.auth import GetCurrentUser
from cruds.users import get_user_by_id, get_users, change_usre_info
from fastapi import APIRouter
from fastapi.params import Depends
from schemas.user import User, UserInfoChangeRequest

user_router = APIRouter()

@user_router.get('/@me')
async def get_me(db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
  return user

@user_router.get('/{user_id}')
async def get_user(user_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
  user = get_user_by_id(db, user_id)
  return user

@user_router.get('')
async def get_user_list(db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
  users = get_users(db)
  return users

@user_router.put('/@me')
async def put_user_info(payload: UserInfoChangeRequest, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
  user = change_usre_info(db, user.id, payload.display_name, payload.profile, payload.avatar_url)
  return user