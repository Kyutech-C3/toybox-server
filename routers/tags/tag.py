from typing import List
from schemas.tag import Tag, BaseTag
from schemas.user import User
from fastapi import APIRouter, HTTPException
from db import get_db
from fastapi.params import Depends
from sqlalchemy.orm import Session
from cruds.users.auth import GetCurrentUser
from cruds.tags.tag import create_tag, get_tag_by_id, get_tags_all, get_tags_by_community_id

tag_router = APIRouter()

@tag_router.post('', response_model=Tag)
async def create_tag(payload: BaseTag, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    tag = create_tag(db, payload.name, payload.color, payload.community_id)
    return tag

@tag_router.get('', response_model=List[Tag])
async def tags_all(limit: int = 10, offset_id: str = None, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    tag_list = get_tags_all(db, limit, offset_id)
    return tag_list

@tag_router.get('/{community_id}', response_model=List[Tag])
async def tags_by_community_id(community_id: str, limit: int = 10, offset_id: str = None, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    tag_list = get_tags_by_community_id(db, limit, offset_id, community_id)
    return tag_list

@tag_router.get('/{tag_id}', response_model=Tag)
async def tag_by_id(tag_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    tag = get_tag_by_id(db, tag_id)
    return tag
