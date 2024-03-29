from fastapi import APIRouter, HTTPException
from fastapi.datastructures import UploadFile
from fastapi.param_functions import File
from fastapi.params import Depends
from sqlalchemy.orm.session import Session

from cruds.users import (
    GetCurrentUser,
    change_user_info,
    get_user_by_id,
    get_users,
    remove_avatar_url,
)
from cruds.works import get_works_by_user_id
from db import get_db, models
from schemas.user import User, UserInfoChangeRequest
from schemas.work import ResWorks
from utils.convert import convert_to_webp_for_avatar
from utils.wasabi import ALLOW_EXTENSIONS, delete_avatar, upload_avatar

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
    extension = file.filename[file.filename.rfind(".") + 1 :].lower()
    if extension not in ALLOW_EXTENSIONS["image"]:
        raise HTTPException(status_code=422, detail="avatar type is invalid")
    file_bin = file.file.read()
    sizes = [64, 128, 256, 512]
    avatar_urls = {}
    for size in sizes:
        converted_bin = convert_to_webp_for_avatar(file_bin, size)
        avatar_urls[str(size)] = upload_avatar(user.id, converted_bin, "webp", size)
    avatar_url = avatar_urls.get("256")
    if avatar_url is None:
        raise HTTPException(status_code=500, detail="upload image failed")
    user_info = change_user_info(db, user_id=user.id, avatar_url=avatar_url)
    return user_info


@user_router.delete("/@me/avatar", response_model=User)
async def delete_user_avatar(
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    if user.avatar_url:
        extension = user.avatar_url[user.avatar_url.rfind(".") + 1 :]
        remove_avatar_url(db, user_id=user.id)
        sizes = [64, 128, 256, 512]
        for size in sizes:
            delete_avatar(user.id, extension, size)
    user = get_user_by_id(db, user.id)
    return user


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
