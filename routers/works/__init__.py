import os
from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from cruds.users.auth import GetCurrentUser
from cruds.works import (delete_work_by_id, get_work_by_id, get_works_by_limit,
                         replace_work, set_work)
from db import get_db, models
from schemas.common import DeleteStatus
from schemas.user import User
from schemas.work import PostWork, ResWorks, Work
from utils.discord import notice_discord

FRONTEND_HOST_URL = os.environ.get("FRONTEND_HOST_URL")
work_router = APIRouter()


@work_router.post("", response_model=Work)
async def post_work(
    payload: PostWork,
    post_discord: bool,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    work = set_work(
        db,
        payload.title,
        payload.description,
        user.id,
        payload.visibility,
        payload.thumbnail_asset_id,
        payload.assets_id,
        payload.urls,
        payload.tags_id,
    )
    if work.visibility != models.Visibility.draft and post_discord:
        notice_discord(
            user_name=work.user.name,
            user_icon_url=work.user.avatar_url,
            work_title=work.title,
            work_description=work.description,
            work_url=f"{FRONTEND_HOST_URL}/works/{work.id}",
            thumbnail_image_url=work.thumbnail.url,
        )
    return work


@work_router.get("", response_model=ResWorks)
async def get_works(
    limit: int = 30,
    visibility: models.Visibility = None,
    oldest_work_id: str = None,
    newest_work_id: str = None,
    tag_names: str = None,
    tag_ids:str = None,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser(auto_error=False)),
    search_word:str= None
):
    works = get_works_by_limit(
        db, limit, visibility, oldest_work_id, newest_work_id,tag_names, tag_ids, user,search_word
    )
    return works


@work_router.get("/{work_id}", response_model=Work)
async def get_work(
    work_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser(auto_error=False)),
):
    user_id = None if user is None else user.id
    work = get_work_by_id(db, work_id, user_id)
    return work


@work_router.put("/{work_id}", response_model=Work)
async def put_work(
    work_id: str,
    payload: PostWork,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    work = replace_work(
        db,
        work_id,
        payload.title,
        payload.description,
        user.id,
        payload.visibility,
        payload.thumbnail_asset_id,
        payload.assets_id,
        payload.urls,
        payload.tags_id,
    )
    return work


@work_router.delete("/{work_id}", response_model=DeleteStatus)
async def delete_work(
    work_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())
):
    user_id = None if user is None else user.id
    result = delete_work_by_id(db, work_id, user_id)
    return result


