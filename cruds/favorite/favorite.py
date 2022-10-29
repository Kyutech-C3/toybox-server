from sqlalchemy.orm.session import Session
from db import models
from schemas.favorite import Favorite,BaseFavorite
from schemas.work import Work
from fastapi import HTTPException

def set_favorite(work_id:str,db:Session,user_id:str) -> Favorite:
    is_work = db.query(models.Work).get(work_id)
    if is_work is None:
        raise HTTPException(
            status_code=404,
            detail="The work_id is not exist"
        )
    if is_work.visibility == models.Visibility.draft:
        raise HTTPException(
            status_code=404,
            detail="The work_id is not exist"
        )
    is_favorite = db.query(models.Favorite).filter(models.Favorite.work_id == work_id).filter(models.Favorite.user_id == user_id).first()
    if is_favorite:
        raise HTTPException(
            status_code=400,
            detail="The favorite is exist"
        )

    favorite_orm = models.Favorite(
        work_id=work_id,
        user_id=user_id
    )
    db.add(favorite_orm)
    db.commit()

    favorite_list = db.query(models.Favorite).filter(models.Favorite.work_id == work_id).all()
    
    favorites = list(map(BaseFavorite.from_orm, favorite_list))

    return Favorite(favorites=favorites, is_favorite=True)

def get_favorite_by_work_id(work_id:str, db:Session, user_id:str) -> Favorite:
    is_work = db.query(models.Work).get(work_id)
    if is_work is None:
        raise HTTPException(
            status_code=404,
            detail="The work_id is not exist"
        )
    if is_work.visibility == models.Visibility.draft:
        raise HTTPException(
            status_code=404,
            detail="The work_id is not exist"
        )
    favorite_by_work_id = db.query(models.Favorite).filter(models.Favorite.work_id == work_id)
    favorite_list = favorite_by_work_id.all()
    favorites = list(map(BaseFavorite.from_orm, favorite_list))
    is_favorite = favorite_by_work_id.filter(models.Favorite.user_id == user_id).first()
    if is_favorite is None:
        return Favorite(favorites=favorites, is_favorite=False)
    else:
        return Favorite(favorites=favorites, is_favorite=True)

def get_favorite_by_user_id(db:Session, user_id:str, auth: bool = False) -> list[Work]:
    favorite_by_user_id_list = db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()
    work_list = []
    for favorite in favorite_by_user_id_list:
        favorite_work = db.query(models.Work).get(favorite.work_id)
        if favorite_work.visibility == models.Visibility.draft:
            continue
        if favorite_work.visibility == models.Visibility.private and not auth:
            continue
        work_list.append(favorite_work)
    
    return work_list

def delete_favorite_by_id(work_id:str, db: Session, user_id:str) -> Favorite:
    is_work = db.query(models.Work).get(work_id)
    if is_work is None:
        raise HTTPException(
            status_code=404,
            detail="The work_id is not exist"
        )
    if is_work.visibility == models.Visibility.draft:
        raise HTTPException(
            status_code=404,
            detail="The work_id is not exist"
        )
    favorite_orm = db.query(models.Favorite).filter(models.Favorite.work_id == work_id).filter(models.Favorite.user_id == user_id).first()
    if favorite_orm is None:
        raise HTTPException(
            status_code=400,
            detail="The favorite is not exist"
        )
    db.delete(favorite_orm)
    db.commit()

    favorite_list = db.query(models.Favorite).filter(models.Favorite.work_id == work_id).all()
    
    favorites = list(map(BaseFavorite.from_orm, favorite_list))

    return Favorite(favorites=favorites, is_favorite=False)


