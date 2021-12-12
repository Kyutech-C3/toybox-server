from typing import List
from sqlalchemy.orm.session import Session
from cruds.works import get_works_by_user_id
from db import get_db
from cruds.users.auth import GetCurrentUser
from cruds.users import get_user_by_id, get_users, change_user_info
from fastapi import APIRouter
from fastapi.params import Depends
from schemas.work import Work
from schemas.user import User, UserInfoChangeRequest

user_router = APIRouter()

@user_router.get('/@me', response_model=User)
async def get_me(db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
  user = get_user_by_id(db, user.id)
  return user

@user_router.get('/{user_id}', response_model=User)
async def get_user(user_id: str, db: Session = Depends(get_db)):
  user = get_user_by_id(db, user_id)
  return user

@user_router.get('', response_model=list[User])
async def get_user_list(limit: int = 30, offset_id: str = None, db: Session = Depends(get_db)):
  users = get_users(db, limit, offset_id)
  return users

@user_router.put('/@me', response_model=User)
async def put_user_info(payload: UserInfoChangeRequest, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
  user = change_user_info(db, user.id, payload.display_name, payload.profile, payload.avatar_url, payload.twitter_id, payload.github_id)
  return user

@user_router.get('/@me/works', response_model=List[Work])
async def get_my_works(db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
  my_works = get_works_by_user_id(db, user.id, True)
  return my_works

@user_router.get('/{user_id}/works', response_model=List[Work])
async def get_users_works(user_id: str, db: Session = Depends(get_db), auth: User = Depends(GetCurrentUser(False))):
  works = get_works_by_user_id(db, user_id, not not auth)
  return works