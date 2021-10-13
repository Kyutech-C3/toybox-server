from typing import List
from schemas.tag import PostTag, GetTag, BaseTag, TagResponsStatus
from schemas.user import User
from fastapi import APIRouter, HTTPException
from db import get_db
from fastapi.params import Depends
from sqlalchemy.orm import Session
from cruds.users.auth import GetCurrentUser
from cruds.tags.tag import create_tag, get_tag_by_id, get_tags, change_tag_by_id, delete_tag_by_id

tag_router = APIRouter()

@tag_router.post('', response_model=GetTag)
async def post_tag(payload: PostTag, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    tag = create_tag(db, payload.name, payload.color, payload.community_id)
    return tag

@tag_router.get('', response_model=List[GetTag])
async def tags_all(community_id: str = None, limit: int = 10, offset_id: str = None, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    tag_list = get_tags(db, limit, offset_id, community_id)
    return tag_list

@tag_router.get('/{tag_id}', response_model=GetTag)
async def tag_by_id(tag_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    tag = get_tag_by_id(db, tag_id)
    return tag

@tag_router.put('/{tag_id}', response_model=GetTag)
async def tag_by_id(tag_id: str, payload: PostTag, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    tag = change_tag_by_id(db, payload.name, payload.community_id, payload.color, tag_id)
    return tag

@tag_router.delete('/{tag_id}', response_model=TagResponsStatus)
async def tag_by_id(tag_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    result = delete_tag_by_id(db, tag_id)
    return result