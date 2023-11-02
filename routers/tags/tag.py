from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from cruds.tags.tag import (
    change_tag_by_id,
    create_tag,
    delete_tag_by_id,
    get_tag_by_id,
    get_tags,
)
from cruds.users.auth import GetCurrentUser
from db import get_db
from schemas.tag import GetTag, PostTag, PutTag, TagResponsStatus
from schemas.user import User

tag_router = APIRouter()


@tag_router.post("", response_model=GetTag)
async def post_tag(
    payload: PostTag,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    tag = create_tag(db, payload.name, payload.color)
    return tag


@tag_router.get("", response_model=List[GetTag])
async def tags_all(
    limit: int = 100,
    smallest_tag_id: str = None,
    biggest_tag_id: str = None,
    w: str = None,
    db: Session = Depends(get_db),
):
    tag_list = get_tags(db, limit, smallest_tag_id, biggest_tag_id, w)
    return tag_list


@tag_router.get("/{tag_id}", response_model=GetTag)
async def get_a_tag(tag_id: str, db: Session = Depends(get_db)):
    tag = get_tag_by_id(db, tag_id)
    return tag


@tag_router.put("/{tag_id}", response_model=GetTag)
async def put_a_tag(
    tag_id: str,
    payload: PutTag,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    tag = change_tag_by_id(db, payload.name, payload.color, tag_id)
    return tag


@tag_router.delete("/{tag_id}", response_model=TagResponsStatus)
async def delete_a_tag(
    tag_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())
):
    result = delete_tag_by_id(db, tag_id)
    return result
