from typing import List, Optional

import markdown
from fastapi import HTTPException
from sqlalchemy import desc, asc, func, or_, case
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import coalesce, count
from sqlalchemy.orm.session import Session

from cruds.assets import delete_asset_by_id
from cruds.url_infos import create_url_info, delete_url_info
from db import models
from schemas.common import DeleteStatus
from schemas.url_info import BaseUrlInfo
from schemas.user import User
from schemas.work import ResWorks, Work

# TODO: CASCADEを導入する

def set_work(
    db: Session,
    title: str,
    description: str,
    user_id: str,
    visibility: str,
    thumbnail_asset_id: str,
    assets_id: List[str],
    urls: List[BaseUrlInfo],
    tags_id: List[str],
) -> Work:
    if title == "":
        raise HTTPException(status_code=400, detail="Title is empty")

    # DB書き込み
    md = markdown.Markdown(extensions=["tables"])
    work_orm = models.Work(
        title=title,
        description=description,
        description_html=md.convert(description),
        user_id=user_id,
        visibility=visibility,
    )
    db.add(work_orm)
    db.commit()
    db.refresh(work_orm)

    # assetのwork_idの更新
    for asset_id in assets_id:
        asset_orm = db.query(models.Asset).get(asset_id)
        if asset_orm is None:
            raise HTTPException(status_code=400, detail="This asset id is invalid.")
        asset_orm.work_id = work_orm.id

    # url_infoテーブルへのインスタンスの作成
    for url in urls:
        create_url_info(
            db, url.get("url"), url.get("url_type", "other"), work_orm.id, user_id
        )

    # tagの中間テーブルへのインスタンスの作成
    for tag_id in tags_id:
        tagging_orm = models.Tagging(work_id=work_orm.id, tag_id=tag_id)
        db.add(tagging_orm)
        db.commit()

    # Thumbnailの中間テーブルへのインスタンスの作成
    if thumbnail_asset_id:
        thumbnail = db.query(models.Asset).get(thumbnail_asset_id)
        if thumbnail is None:
            raise HTTPException(
                status_code=400, detail="This thumbnail asset id is invalid."
            )
        thumbnail_orm = models.Thumbnail(work_id=work_orm.id, asset_id=thumbnail.id)
        db.add(thumbnail_orm)
        db.commit()

    # schemaに変換
    db.refresh(work_orm)
    work = Work.from_orm(work_orm)
    work.is_favorite = False
    work.favorite_count = 0

    return work


def get_works_by_limit(
    db: Session,
    limit: int,
    visibility: models.Visibility,
    oldest_work_id: str,
    newest_work_id: str,
    tag_names: str,
    tag_ids: str,
    user: Optional[User],
    search_word:str,
    order_by:str = 'created_at',
    order:str = 'asc'
) -> ResWorks:
    if tag_names != None and tag_ids != None:
        raise HTTPException(
            status_code=422, detail="tag name and ID cannot be specified at the same time."
        )

    favorite_count_subquery = db.query(models.Favorite.work_id, count(models.Favorite.work_id).label('favorite_count')).group_by(models.Favorite.work_id).subquery('favorite_count_subquery')

    is_favorite_subquery = None
    if user is not None:
        is_favorite_subquery = db.query(models.Favorite.work_id, models.Favorite.user_id.label('is_favorite_flag')).filter(models.Work.id == models.Favorite.work_id, models.Favorite.user_id == user.id).subquery('is_favorite_subquery')

    works_orm = (
        db.query(
            models.Work,
            coalesce(favorite_count_subquery.c.favorite_count, 0).label('favorite_count'),
            case([(is_favorite_subquery.c.is_favorite_flag == None, False)], else_=True).label('is_favorite') if is_favorite_subquery is not None else False
        )
        .join(models.User,models.Work.user_id==models.User.id)
        .join(models.Tagging,models.Work.id==models.Tagging.work_id)
        .join(models.Tag,models.Tagging.tag_id==models.Tag.id)
        .outerjoin(favorite_count_subquery, models.Work.id==favorite_count_subquery.c.work_id)
        .filter(models.Work.visibility != models.Visibility.draft)
    )

    if is_favorite_subquery is not None:
        works_orm = works_orm.outerjoin(is_favorite_subquery, models.Work.id==is_favorite_subquery.c.work_id)

    # order_byの指定
    if order_by == 'created_at':
        column_of_order_by = models.Work.created_at
    elif order_by == 'updated_at':
        column_of_order_by = models.Work.updated_at
    elif order_by == 'favorite_count':
        column_of_order_by = favorite_count_subquery.c.favorite_count
    elif order_by == 'comment':
        column_of_order_by = models.Work.comment_count
    else:
        column_of_order_by = models.Work.created_at
    
    # orderの指定
    if order == 'desc':
        print('desc')
        works_orm = works_orm.order_by(desc(column_of_order_by))
        print(works_orm)
    else:
        print('asc')
        works_orm = works_orm.order_by(asc(column_of_order_by))
        print(works_orm)
    
    work_orm = works_orm.group_by(models.Work.id)

    # search_by_free_word
    if search_word:
        works_orm = works_orm.filter(or_(models.User.name.ilike(f"%{search_word}%"),models.Tag.name.ilike(f"%{search_word}%"),models.Work.title.ilike(f"%{search_word}%")))

    # search_by_tag_ids
    if tag_ids:
        tag_id_list = tag_ids.split(",")
        works_orm = works_orm.filter(models.Tagging.tag_id.in_(tag_id_list)).filter(
            models.Tagging.work_id == models.Work.id
        )
        works_orm = works_orm.group_by(models.Work.id).having(
            func.count(models.Work.id) == len(tag_id_list)
        )

    # search_by_tag_names
    if tag_names:
        tag_name_list = tag_names.split(",")
        works_orm = works_orm.filter(models.Tag.name.in_(tag_name_list)).filter(
            models.Tagging.work_id == models.Work.id
        )
        works_orm = works_orm.group_by(models.Work.id).having(
            func.count(models.Work.id) == len(tag_name_list)
        )

    # check user
    if user is None:
        works_orm = works_orm.filter(models.Work.visibility == models.Visibility.public)
    elif visibility is not None:
        works_orm = works_orm.filter(models.Work.visibility == visibility)

    # get works total count
    works_total_count = works_orm.count()

    # pagination
    if oldest_work_id:
        oldest_work = (
            db.query(models.Work).filter(models.Work.id == oldest_work_id).first()
        )
        if oldest_work is None:
            raise HTTPException(status_code=400, detail="this oldest_id is invalid")
        works_orm = works_orm.filter(models.Work.created_at > oldest_work.created_at)
    if newest_work_id:
        newest_work = (
            db.query(models.Work).filter(models.Work.id == newest_work_id).first()
        )
        if newest_work is None:
            raise HTTPException(status_code=400, detail="this newest_id is invalid")
        works_orm = works_orm.filter(models.Work.created_at < newest_work.created_at)
    
    works_orm = works_orm.limit(limit).all()

    works = list(map(lambda work_orm: Work(
        id=work_orm[0].id,
        title=work_orm[0].title,
        description=work_orm[0].description,
        description_html=work_orm[0].description_html,
        user=work_orm[0].user,
        assets=work_orm[0].assets,
        urls=work_orm[0].urls,
        visibility=work_orm[0].visibility,
        tags=work_orm[0].tags,
        thumbnail=work_orm[0].thumbnail,
        created_at=work_orm[0].created_at,
        updated_at=work_orm[0].updated_at,
        comments=work_orm[0].comments,
        favorite_count=work_orm[1],
        is_favorite=work_orm[2]
    ), works_orm))

    resWorks = ResWorks(works=works, works_total_count=works_total_count)
    return resWorks


def get_work_by_id(db: Session, work_id: str, user_id: Optional[str]) -> Work:
    work_orm = db.query(models.Work).get(work_id)
    if (work_orm is None) or (
        work_orm.visibility == models.Visibility.draft and user_id != work_orm.user_id
    ):
        raise HTTPException(status_code=404, detail="work is not found")
    if work_orm.visibility == models.Visibility.private and user_id is None:
        raise HTTPException(
            status_code=403, detail="This work is a private work. You need to sign in."
        )
    work = Work.from_orm(work_orm)
    if user_id is not None:
        work.is_favorite = (
            db.query(models.Favorite)
            .filter(
                models.Favorite.work_id == work.id, models.Favorite.user_id == user_id
            )
            .first()
            is not None
        )
    else:
        work.is_favorite = False
    work.favorite_count = (
        db.query(models.Favorite).filter(models.Favorite.work_id == work.id).count()
    )
    return work


def replace_work(
    db: Session,
    work_id: str,
    title: str,
    description: str,
    user_id: str,
    visibility: str,
    thumbnail_asset_id: str,
    assets_id: List[str],
    urls: List[BaseUrlInfo],
    tags_id: List[str],
) -> Work:
    work_orm = db.query(models.Work).get(work_id)

    # 自分のWorkでなければ弾く
    if work_orm.user_id != user_id:
        raise HTTPException(status_code=401, detail="this work's author isn't you")

    # titleのvalidator
    if title == "":
        raise HTTPException(status_code=400, detail="Title is empty")

    # DB更新
    md = markdown.Markdown(extensions=["tables"])
    work_orm.title = title
    work_orm.description = description
    work_orm.description_html = md.convert(description)
    work_orm.visibility = visibility
    db.add(work_orm)
    db.commit()
    db.refresh(work_orm)

    # 古いassetのwork_idの削除
    assets_orm = db.query(models.Asset).filter(models.Asset.work_id == work_id).all()
    for asset_orm in assets_orm:
        asset_orm.work_id = None
        db.commit()
        db.refresh(asset_orm)

    # 使われなくなったassetの削除
    old_asset_ids = [asset_orm.id for asset_orm in assets_orm]
    old_thumbnail_orm = (
        db.query(models.Thumbnail).filter(models.Thumbnail.work_id == work_id).first()
    )
    if old_thumbnail_orm:
        old_asset_ids.append(old_thumbnail_orm.asset_id)
    new_asset_ids = assets_id[:]
    if thumbnail_asset_id:
        new_asset_ids.append(thumbnail_asset_id)
    delete_asset_ids = set(old_asset_ids) - set(new_asset_ids)
    for delete_asset_id in delete_asset_ids:
        db.query(models.Asset).get(delete_asset_id).work_id = None

    # assetのwork_idの更新
    for asset_id in assets_id:
        asset_orm = db.query(models.Asset).get(asset_id)
        if asset_orm is None:
            raise HTTPException(status_code=400, detail="This asset id is invalid.")
        asset_orm.work_id = work_id

    # url_infoの削除
    urls_orm = db.query(models.UrlInfo).filter(models.UrlInfo.work_id == work_id).all()
    for url_orm in urls_orm:
        delete_url_info(db, url_orm.id)

    # url_infoテーブルへのインスタンスの作成
    for url in urls:
        create_url_info(
            db, url.get("url"), url.get("url_type", "other"), work_id, user_id
        )

    # tagの中間テーブルのインスタンスの削除
    taggings_orm = (
        db.query(models.Tagging).filter(models.Tagging.work_id == work_id).all()
    )
    for tagging in taggings_orm:
        db.delete(tagging)
    db.commit()

    # tagの中間テーブルへのインスタンスの作成
    for tag_id in tags_id:
        tagging_orm = models.Tagging(work_id=work_id, tag_id=tag_id)
        db.add(tagging_orm)
        db.commit()

    # Thumbnailの中間テーブルへのインスタンスの作成
    if thumbnail_asset_id:
        if old_thumbnail_orm:
            db.delete(old_thumbnail_orm)
            db.commit()
        thumbnail = db.query(models.Asset).get(thumbnail_asset_id)
        if thumbnail is None:
            raise HTTPException(
                status_code=400, detail="This thumbnail asset id is invalid."
            )
        new_thumbnail_orm = models.Thumbnail(
            work_id=work_id, asset_id=thumbnail_asset_id
        )
        db.add(new_thumbnail_orm)
        db.commit()

    # schemaに変換
    db.refresh(work_orm)
    work = Work.from_orm(work_orm)
    work.is_favorite = (
        db.query(models.Favorite)
        .filter(models.Favorite.work_id == work.id, models.Favorite.user_id == user_id)
        .first()
        is not None
    )
    work.favorite_count = (
        db.query(models.Favorite).filter(models.Favorite.work_id == work.id).count()
    )

    return work


def delete_work_by_id(db: Session, work_id: str, user_id: str) -> DeleteStatus:
    work_orm = db.query(models.Work).get(work_id)
    if work_orm.user_id != user_id:
        raise HTTPException(status_code=403, detail="cannot delete other's work")

    assets_orm = db.query(models.Asset).filter(models.Asset.work_id == work_id).all()
    urls_orm = db.query(models.UrlInfo).filter(models.UrlInfo.work_id == work_id).all()

    for asset_orm in assets_orm:
        asset_orm.work_id = None

    for url_orm in urls_orm:
        delete_url_info(db, url_orm.id)

    db.delete(work_orm)
    db.commit()

    return {"status": "OK"}


def get_works_by_user_id(
    db: Session,
    user_id: str,
    visibility: models.Visibility,
    oldest_work_id: str,
    newest_work_id: str,
    limit: int,
    tags: str,
    user: Optional[User],
) -> ResWorks:
    user_orm = db.query(models.User).get(user_id)
    if user_orm is None:
        raise HTTPException(status_code=404, detail="this user is not exist")

    works_orm = (
        db.query(models.Work)
        .order_by(desc(models.Work.created_at))
        .filter(models.Work.user_id == user_id)
    )

    if tags:
        tag_list = tags.split(",")
        works_orm = works_orm.filter(models.Tagging.tag_id.in_(tag_list)).filter(
            models.Tagging.work_id == models.Work.id
        )
        works_orm = works_orm.group_by(models.Work.id).having(
            func.count(models.Work.id) == len(tag_list)
        )

    if user is None:
        works_orm = works_orm.filter(models.Work.visibility == models.Visibility.public)
    elif user.id != user_id:
        works_orm = works_orm.filter(models.Work.visibility != models.Visibility.draft)

    if visibility is not None:
        works_orm = works_orm.filter(models.Work.visibility == visibility)

    works_total_count = works_orm.count()

    if oldest_work_id:
        oldest_work = (
            db.query(models.Work).filter(models.Work.id == oldest_work_id).first()
        )
        if oldest_work is None:
            raise HTTPException(status_code=400, detail="oldest work is not found")
        works_orm = works_orm.filter(models.Work.created_at > oldest_work.created_at)

    if newest_work_id:
        newest_work = (
            db.query(models.Work).filter(models.Work.id == newest_work_id).first()
        )
        if newest_work is None:
            raise HTTPException(status_code=400, detail="newest work is not found")
        works_orm = works_orm.filter(models.Work.created_at < newest_work.created_at)

    works_orm = works_orm.limit(limit).all()

    works = []
    for work_orm in works_orm:
        work = Work.from_orm(work_orm)
        if user is not None:
            work.is_favorite = (
                db.query(models.Favorite)
                .filter(
                    models.Favorite.work_id == work.id,
                    models.Favorite.user_id == user.id,
                )
                .first()
                is not None
            )
        else:
            work.is_favorite = False
        work.favorite_count = (
            db.query(models.Favorite).filter(models.Favorite.work_id == work.id).count()
        )
        works.append(work)

    resWorks = ResWorks(works=works, works_total_count=works_total_count)
    return resWorks
