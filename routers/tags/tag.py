from schemas.tag import Tag, BaseTag
from schemas.user import User
from fastapi import APIRouter, HTTPException
from db import get_db
from fastapi.params import Depends
from sqlalchemy.orm import Session
from cruds.users.auth import GetCurrentUser
from cruds.tags.tag import create_tag, get_tag

tag_router = APIRouter()

@tag_router.post('', response_model=Tag)
async def post_tag(payload: BaseTag, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    tag = create_tag(db, payload.name, payload.color, payload.community_id)
    return tag


@tag_router.get('/{tag_id}', response_model=Tag)
async def post_tag(tag_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    tag = get_tag(db, tag_id)
    return tag
