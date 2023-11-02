from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from cruds.favorite.favorite import (
    delete_favorite_by_id,
    get_favorite_by_user_id,
    get_favorite_by_work_id,
    set_favorite,
)
from cruds.users.auth import GetCurrentUser
from db import get_db
from schemas.favorite import Favorite
from schemas.user import User
from schemas.work import Work

favorite_router = APIRouter()
user_favorite_router = APIRouter()


@favorite_router.post("/{work_id}/favorite", response_model=Favorite)
async def post_favorite(
    work_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())
):
    favorites = set_favorite(work_id, db, user.id)
    return favorites


@favorite_router.get("/{work_id}/favorite", response_model=Favorite)
async def favorite_by_work_id(
    work_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())
):
    favorites = get_favorite_by_work_id(work_id, db, user.id)
    return favorites


@user_favorite_router.get("/@me/favorite", response_model=list[Work])
async def get_my_favorite(
    user: User = Depends(GetCurrentUser()), db: Session = Depends(get_db)
):
    favorites = get_favorite_by_user_id(db, user.id, user)
    return favorites


@user_favorite_router.get("/{user_id}/favorite", response_model=list[Work])
async def get_a_user_favorite(
    user_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser(False)),
):
    favorites = get_favorite_by_user_id(db, user_id, user)
    return favorites


@favorite_router.delete("/{work_id}/favorite", response_model=Favorite)
async def delete_favorite(
    work_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())
):
    favorites = delete_favorite_by_id(work_id, db, user.id)
    return favorites
