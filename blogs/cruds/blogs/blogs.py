from fastapi import HTTPException
from sqlalchemy.orm import Session

from blogs.db import models as blog_models
from blogs.schemas import Blog
from db import models
from db.enums import Visibility


def create_blog(
    db: Session,
    title: str,
    body_text: str,
    user_id: str,
    visibility: Visibility,
    thumbnail_asset_id: str,
    assets_id: str,
    tags_id: str,
) -> Blog:
    if title == "":
        raise HTTPException(status_code=400, detail="title is empty")

    # DB書き込み
    blog_orm = blog_models.Blog(
        title=title,
        body_text=body_text,
        user_id=user_id,
        visibility=visibility,
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
    blog.is_favorite = False
    blog.favorite_count = 0

    return blog
