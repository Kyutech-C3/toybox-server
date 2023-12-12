from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from blogs.cruds.blogs import (
    create_blog,
    delete_blog_by_id,
    get_blog_by_id,
    get_blogs_pagination,
    replace_blog,
)
from blogs.schemas import Blog, BlogsResponse, PostBlog
from cruds.users import GetCurrentUser
from db import Visibility, get_db
from schemas.common import DeleteStatus
from schemas.user import User

blog_router = APIRouter()
users_blog_router = APIRouter()


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
        payload.published_at,
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
        limit,
        page,
        visibility,
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


@users_blog_router.get("/@me/blogs", response_model=BlogsResponse)
async def get_my_blog(
    limit: int = 30,
    page: int = 1,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    blog = get_blogs_pagination(
        db, limit, page, user_id=user.id, searched_user_id=user.id
    )
    return blog


@blog_router.delete("/{blog_id}", response_model=DeleteStatus)
async def delete_blog(
    blog_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    result = delete_blog_by_id(db, blog_id, user.id)
    return result


@blog_router.put("/{blog_id}", response_model=Blog)
async def put_blog(
    blog_id: str,
    payload: PostBlog,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    blog = replace_blog(
        db,
        blog_id,
        user.id,
        payload.title,
        payload.body_text,
        payload.visibility,
        payload.thumbnail_asset_id,
        payload.assets_id,
        payload.tags_id,
        payload.published_at,
    )
    return blog
