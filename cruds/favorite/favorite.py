from typing import Optional
from sqlalchemy.orm.session import Session
from db import models
from schemas.favorite import Favorite, BaseFavorite
from schemas.user import User
from schemas.work import Work
from fastapi import HTTPException


def set_favorite(work_id: str, db: Session, user_id: str) -> Favorite:
    is_work = db.query(models.Work).get(work_id)
    if is_work is None:
        raise HTTPException(status_code=404, detail="The work_id is not exist")
    if is_work.visibility == models.Visibility.draft:
        raise HTTPException(status_code=404, detail="The work_id is not exist")
    is_favorite = (
        db.query(models.Favorite)
        .filter(models.Favorite.work_id == work_id)
        .filter(models.Favorite.user_id == user_id)
        .first()
    )
    if is_favorite:
        raise HTTPException(status_code=400, detail="The favorite is exist")

    favorite_orm = models.Favorite(work_id=work_id, user_id=user_id)
    db.add(favorite_orm)
    db.commit()

    favorite_list = (
        db.query(models.Favorite).filter(models.Favorite.work_id == work_id).all()
    )

    favorites = list(map(BaseFavorite.from_orm, favorite_list))

    return Favorite(
        favorites=favorites, is_favorite=True, favorite_count=len(favorites)
    )


def get_favorite_by_work_id(work_id: str, db: Session, user_id: str) -> Favorite:
    is_work = db.query(models.Work).get(work_id)
    if is_work is None:
        raise HTTPException(status_code=404, detail="The work_id is not exist")
    if is_work.visibility == models.Visibility.draft:
        raise HTTPException(status_code=404, detail="The work_id is not exist")
    favorite_by_work_id = db.query(models.Favorite).filter(
        models.Favorite.work_id == work_id
    )
    favorite_list = favorite_by_work_id.all()
    favorites = list(map(BaseFavorite.from_orm, favorite_list))
    is_favorite = favorite_by_work_id.filter(models.Favorite.user_id == user_id).first()
    return Favorite(
        favorites=favorites,
        is_favorite=is_favorite is not None,
        favorite_count=len(favorites),
    )


def get_favorite_by_user_id(
    db: Session, user_id: str, user: Optional[User]
) -> list[Work]:
    favorite_by_user_id_list = (
        db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()
    )
    work_list = []
    for favorite in favorite_by_user_id_list:
        favorite_work = db.query(models.Work).get(favorite.work_id)
        if favorite_work.visibility == models.Visibility.draft:
            continue
        if favorite_work.visibility == models.Visibility.private and user is not None:
            continue
        work = Work.from_orm(favorite_work)
        if user is not None:
            work.is_favorite = (
                db.query(models.Favorite)
                .filter(
                    models.Favorite.work_id == favorite.work_id,
                    models.Favorite.user_id == user.id,
                )
                .first()
                is not None
            )
        else:
            work.is_favorite = False
        work.favorite_count = (
            db.query(models.Favorite)
            .filter(models.Favorite.work_id == favorite_work.id)
            .count()
        )
        work_list.append(work)

    return work_list


def delete_favorite_by_id(work_id: str, db: Session, user_id: str) -> Favorite:
    is_work = db.query(models.Work).get(work_id)
    if is_work is None:
        raise HTTPException(status_code=404, detail="The work_id is not exist")
    if is_work.visibility == models.Visibility.draft:
        raise HTTPException(status_code=404, detail="The work_id is not exist")
    favorite_orm = (
        db.query(models.Favorite)
        .filter(models.Favorite.work_id == work_id)
        .filter(models.Favorite.user_id == user_id)
        .first()
    )
    if favorite_orm is None:
        raise HTTPException(status_code=400, detail="The favorite is not exist")
    db.delete(favorite_orm)
    db.commit()

    favorite_list = (
        db.query(models.Favorite).filter(models.Favorite.work_id == work_id).all()
    )

    favorites = list(map(BaseFavorite.from_orm, favorite_list))

    return Favorite(
        favorites=favorites, is_favorite=False, favorite_count=len(favorites)
    )
