from schemas.work import PostWork, Work
from schemas.user import User
from fastapi import APIRouter
from db import get_db
from fastapi.params import Depends
from sqlalchemy.orm import Session
from cruds.users.auth import GetCurrentUser
from cruds.works import get_work_by_id, get_works_by_limit, set_work
from typing import List

work_router = APIRouter()

@work_router.post('', response_model=Work)
async def post_work(payload: PostWork, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    work = set_work(db, payload.title, payload.description, user.id, payload.community_id, 
        payload.visibillity, payload.thumbnail_asset_id, payload.assets_id, payload.urls)
    return work

@work_router.get('', response_model=List[Work])
async def get_works(limit: int = 30, oldest_id: str = None, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser(auto_error=False))):
    auth = user is not None
    works = get_works_by_limit(db, limit, oldest_id, auth=auth)
    return works

@work_router.get('/{work_id}', response_model=Work)
async def get_work(work_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser(auto_error=False))):
    auth = user is not None
    work = get_work_by_id(db, work_id, auth=auth)
    return work
