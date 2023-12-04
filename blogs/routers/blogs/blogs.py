from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from blogs.cruds.blogs import create_blog, get_blog_by_id, get_blogs_pagination
from blogs.schemas import Blog, BlogsResponse, PostBlog
from cruds.users import GetCurrentUser
from db import Visibility, get_db
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


@blog_router.get("", response_model=BlogsResponse)
async def get_blogs(
    visibility: Visibility = None,
    limit: int = 30,
    page: int = 1,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser(auto_error=False)),
):
    user_id = user.id if user is not None else None
    blogs = get_blogs_pagination(
        db,
        visibility,
        limit,
        page,
        user_id,
    )
    return blogs


@blog_router.get("/{blog_id}", response_model=Blog)
async def get_blog(
    blog_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser(auto_error=False)),
):
    user_id = user.id if user is not None else None
    blog = get_blog_by_id(db, blog_id, user_id)
    return blog
