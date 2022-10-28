from db import get_db
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from schemas.favorite import Favorite
from schemas.user import User
from cruds.users.auth import GetCurrentUser
from cruds.favorite.favorite import set_favorite

favorite_router = APIRouter()

@favorite_router.post("/{work_id}/favorite",response_model=Favorite)
async def post_favorite(work_id:str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    try:
        user_id = user.id
    except AttributeError:
        user_id = None
    favorites = set_favorite(work_id, db, user_id)
    return favorites