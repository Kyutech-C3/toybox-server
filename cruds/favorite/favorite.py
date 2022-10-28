from sqlalchemy.orm.session import Session
from db import models
from schemas.favorite import Favorite,BaseFavorite

def set_favorite(work_id:str,db:Session,user_id:str) -> Favorite:
    favorite_orm = models.Favorite(
        work_id=work_id,
        user_id=user_id
    )
    db.add(favorite_orm)
    db.commit()

    favorite_list = db.query(models.Favorite).filter(models.Favorite.work_id == work_id).all()
    
    favorites = list(map(BaseFavorite.from_orm, favorite_list))

    return Favorite(favorites=favorites, is_favorite=True)

