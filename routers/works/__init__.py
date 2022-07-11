from schemas.common import DeleteStatus
from schemas.work import PostWork, SearchOption, Work
from schemas.user import User
from fastapi import APIRouter
from db import get_db
from fastapi.params import Depends
from sqlalchemy.orm import Session
from cruds.users.auth import GetCurrentUser
from cruds.works import delete_work_by_id, get_work_by_id, get_works_by_limit, replace_work, search_work_by_option, set_work
from typing import List

work_router = APIRouter()

@work_router.post('', response_model=Work)
async def post_work(payload: PostWork, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    work = set_work(db, payload.title, payload.description, user.id, 
                    payload.visibility, payload.thumbnail_asset_id, payload.assets_id, payload.urls, payload.tags_id)
    return work

@work_router.get('', response_model=List[Work])
async def get_works(limit: int = 30, oldest_id: str = None, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser(auto_error=False))):
    auth = user is not None
    works = get_works_by_limit(db, limit, oldest_id, auth=auth)
    return works

@work_router.get('/search', response_model=list[Work])
async def search_work(payload: SearchOption, limit: int = 30, oldest_id: str = None, user: User = Depends(GetCurrentUser(auto_error=False)), db: Session = Depends(get_db)):
    auth = user is not None
    works = search_work_by_option(db, limit, oldest_id, payload.tags, auth)
    return works

@work_router.get('/{work_id}', response_model=Work)
async def get_work(work_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser(auto_error=False))):
    auth = user is not None
    work = get_work_by_id(db, work_id, auth=auth)
    return work

@work_router.put('/{work_id}', response_model=Work)
async def put_work(work_id: str, payload: PostWork, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    work = replace_work(db, work_id, payload.title, payload.description, user.id, 
                        payload.visibility, payload.thumbnail_asset_id, payload.assets_id, payload.urls, 
                        payload.tags_id)
    return work

@work_router.delete('/{work_id}', response_model=DeleteStatus, dependencies=[Depends(GetCurrentUser())])
async def delete_work(work_id: str, db: Session = Depends(get_db)):
    result = delete_work_by_id(db, work_id)
    return result