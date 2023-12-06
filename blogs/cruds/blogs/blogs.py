from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from blogs.db import models as blog_models
from blogs.schemas import Blog, BlogsResponse
from db import models
from db.enums import Visibility
from utils.wasabi import get_asset_url


def create_blog(
    db: Session,
    title: str,
    body_text: str,
    user_id: str,
    visibility: Visibility,
    thumbnail_asset_id: str,
    assets_id: list[str],
    tags_id: list[str],
    published_at: Optional[datetime],
) -> Blog:
    if title == "":
        raise HTTPException(status_code=400, detail="title is empty")

    # DB書き込み
    blog_orm = blog_models.Blog(
        title=title,
        body_text=body_text,
        user_id=user_id,
        visibility=visibility,
        published_at=published_at,
    )
    db.add(blog_orm)
    db.commit()
    db.refresh(blog_orm)

    # assetのwork_idの更新
    for asset_id in assets_id:
        asset_orm = db.query(blog_models.BlogAsset).get(asset_id)
        if asset_orm is None:
            raise HTTPException(
                status_code=400, detail=f'asset_id "{assets_id}" is not exist'
            )
        asset_orm.blog_id = blog_orm.id

    # tagの中間テーブルへのインスタンスの作成
    for tag_id in tags_id:
        tag_orm = db.query(models.Tag).get(tag_id)
        if tag_orm is None:
            raise HTTPException(
                status_code=400, detail=f'tag_id "{assets_id}" is not exist'
            )
        tagging_orm = blog_models.BlogTagging(blog_id=blog_orm.id, tag_id=tag_id)
        db.add(tagging_orm)
        db.commit()

    # Thumbnailの中間テーブルへのインスタンスの作成
    if thumbnail_asset_id:
        thumbnail = db.query(blog_models.BlogAsset).get(thumbnail_asset_id)
        if thumbnail is None:
            raise HTTPException(
                status_code=400,
                detail=f'thumbnail_asset_id "{thumbnail_asset_id}" is invalid',
            )
        thumbnail_orm = blog_models.BlogThumbnail(
            blog_id=blog_orm.id, asset_id=thumbnail.id
        )
        db.add(thumbnail_orm)
        db.commit()

    # schemaに変換
    db.refresh(blog_orm)
    blog = Blog.from_orm(blog_orm)

    # url生成
    for i, asset in enumerate(blog.assets):
        blog.assets[i].url = get_asset_url(asset.id, asset.extension, True)
    blog.thumbnail.url = get_asset_url(
        blog.thumbnail.id, blog.thumbnail.extension, True
    )

    blog.is_favorite = False
    blog.favorite_count = 0

    return blog


def get_blogs_pagination(
    db: Session,
    limit: int,
    page: int,
    visibility: Optional[Visibility] = None,
    user_id: Optional[str] = None,
    searched_user_id: Optional[str] = None,
) -> BlogsResponse:
    blogs_orm = (
        db.query(blog_models.Blog)
        .join(models.User, blog_models.Blog.user_id == models.User.id)
        .join(
            blog_models.BlogTagging,
            blog_models.Blog.id == blog_models.BlogTagging.blog_id,
        )
        .join(models.Tag, blog_models.BlogTagging.tag_id == models.Tag.id)
        .group_by(blog_models.Blog.id)
        .order_by(desc(blog_models.Blog.created_at))
    )
    if user_id != searched_user_id:
        blogs_orm = blogs_orm.filter(blog_models.Blog.visibility != Visibility.draft)
    if user_id is None:
        blogs_orm = blogs_orm.filter(blog_models.Blog.visibility == Visibility.public)
    elif visibility is not None:
        blogs_orm = blogs_orm.filter(blog_models.Blog.visibility == visibility)
    if searched_user_id is not None:
        blogs_orm = blogs_orm.filter(blog_models.Blog.user_id == searched_user_id)

    blogs_total_count = blogs_orm.count()

    offset = limit * (page - 1)
    blogs_orm = blogs_orm.offset(offset).limit(limit).all()

    blogs = []
    for blog_orm in blogs_orm:
        blog = Blog.from_orm(blog_orm)
        blog.is_favorite = False
        if user_id is not None:
            blog.is_favorite = (
                db.query(blog_models.BlogFavorite)
                .filter(
                    blog_models.BlogFavorite.blog_id == blog.id,
                    blog_models.BlogFavorite.user_id == user_id,
                )
                .first()
                is not None
            )
        blog.favorite_count = (
            db.query(blog_models.BlogFavorite)
            .filter(blog_models.BlogFavorite.blog_id == blog.id)
            .count()
        )
        # url生成
        for i, asset in enumerate(blog.assets):
            blog.assets[i].url = get_asset_url(asset.id, asset.extension, True)
        blog.thumbnail.url = get_asset_url(
            blog.thumbnail.id, blog.thumbnail.extension, True
        )
        blogs.append(blog)

    response = BlogsResponse(blogs=blogs, blogs_total_count=blogs_total_count)
    return response


def get_blog_by_id(db: Session, blog_id: str, user_id: str) -> Blog:
    blog_orm = db.query(blog_models.Blog).get(blog_id)
    if (blog_orm is None) or (
        blog_orm.visibility == Visibility.draft and user_id != blog_orm.user_id
    ):
        raise HTTPException(status_code=404, detail="work is not found")
    if blog_orm.visibility == Visibility.private and user_id is None:
        raise HTTPException(status_code=403, detail="this work is a private blog")
    blog = Blog.from_orm(blog_orm)
    blog.is_favorite = False
    if user_id is not None:
        blog.is_favorite = (
            db.query(blog_models.BlogFavorite)
            .filter(
                blog_models.BlogFavorite.blog_id == blog.id,
                blog_models.BlogFavorite.user_id == user_id,
            )
            .first()
            is not None
        )
    blog.favorite_count = (
        db.query(blog_models.BlogFavorite)
        .filter(blog_models.BlogFavorite.blog_id == blog.id)
        .count()
    )
    # url生成
    for i, asset in enumerate(blog.assets):
        blog.assets[i].url = get_asset_url(asset.id, asset.extension, True)
    blog.thumbnail.url = get_asset_url(
        blog.thumbnail.id, blog.thumbnail.extension, True
    )
    return blog
