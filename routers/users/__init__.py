from typing import List
from sqlalchemy.orm.session import Session
from cruds.works import get_works_by_user_id
from db import get_db
from cruds.users.auth import GetCurrentUser
from cruds.users import get_user_by_id, get_users, change_user_info, remove_avatar_url
from fastapi import APIRouter
from fastapi.params import Depends
from schemas.work import Work, ResWorks
from schemas.user import User, UserInfoChangeRequest
from schemas.common import DeleteStatus
from fastapi.datastructures import UploadFile
from fastapi.param_functions import File, Form
from db import models
from utils.wasabi import upload_avatar, delete_avatar

user_router = APIRouter()


@user_router.get("/@me", response_model=User)
async def get_me(db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    user = get_user_by_id(db, user.id)
    return user


@user_router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    return user


@user_router.get("", response_model=list[User])
async def get_user_list(
    limit: int = 30,
    oldest_user_id: str = None,
    newest_user_id: str = None,
    db: Session = Depends(get_db),
):
    users = get_users(db, limit, oldest_user_id, newest_user_id)
    return users


@user_router.put("/@me", response_model=User)
async def put_user_info(
    payload: UserInfoChangeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    user_info = change_user_info(
        db,
        user_id=user.id,
        display_name=payload.display_name,
        profile=payload.profile,
        twitter_id=payload.twitter_id,
        github_id=payload.github_id,
    )
    return user_info


@user_router.put("/@me/avatar", response_model=User)
async def update_user_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    old_extension = user.avatar_url[user.avatar_url.rfind(".") + 1 :]
    delete_avatar(user.id, old_extension)
    new_extension = file.filename[file.filename.rfind(".") + 1 :]
    avatar_url = upload_avatar(user.id, file.file, new_extension)
    user_info = change_user_info(db, user_id=user.id, avatar_url=avatar_url)
    return user_info


@user_router.delete("/@me/avatar", response_model=DeleteStatus)
async def delete_user_avatar(
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    if user.avatar_url:
        extension = user.avatar_url[user.avatar_url.rfind(".") + 1 :]
        remove_avatar_url(db, user_id=user.id)
        delete_avatar(user.id, extension)
    return {"status": "OK"}


@user_router.get("/@me/works", response_model=ResWorks)
async def get_my_works(
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
    visibility: models.Visibility = None,
    oldest_user_id: str = None,
    newest_user_id: str = None,
    tags: str = None,
    limit: int = 30,
):
    my_works = get_works_by_user_id(
        db, user.id, visibility, oldest_user_id, newest_user_id, limit, tags, user
    )
    return my_works


@user_router.get("/{user_id}/works", response_model=ResWorks)
async def get_users_works(
    user_id: str,
    oldest_user_id: str = None,
    newest_user_id: str = None,
    limit: int = 30,
    tags: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser(False)),
    visibility: models.Visibility = None,
):
    works = get_works_by_user_id(
        db, user_id, visibility, oldest_user_id, newest_user_id, limit, tags, user
    )
    return works
