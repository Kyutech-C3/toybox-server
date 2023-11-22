from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from blogs.cruds.blogs import create_blog
from blogs.schemas import Blog, PostBlog
from cruds.users import GetCurrentUser
from db import get_db
from schemas.user import User

blog_router = APIRouter()


@blog_router.post("", response_model=Blog)
async def post_blog(
    payload: PostBlog,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    work = create_blog(
        db,
        payload.title,
        payload.body_text,
        user.id,
        payload.visibility,
        payload.thumbnail_asset_id,
        payload.assets_id,
        payload.tags_id,
    )
    return work
