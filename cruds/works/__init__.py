from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import desc, func
from cruds.assets import delete_asset_by_id
from cruds.url_infos import create_url_info, delete_url_info
from db import models
from sqlalchemy.orm.session import Session
from schemas.common import DeleteStatus
from schemas.url_info import BaseUrlInfo
from schemas.work import Work
import markdown

# TODO: CASCADEを導入する

def set_work(db: Session, title: str, description: str, user_id: str, 
             visibility: str, thumbnail_asset_id: str,
             assets_id: List[str], urls: List[BaseUrlInfo], tags_id: List[str]) -> Work:
    

    if title == '':
        raise HTTPException(status_code=400, detail="Title is empty")

    # DB書き込み
    md = markdown.Markdown(extensions=['tables'])
    work_orm = models.Work(
        title = title,
        description = description,
        description_html = md.convert(description),
        user_id = user_id,
        visibility = visibility,
    )
    db.add(work_orm)
    db.commit()
    db.refresh(work_orm)

    # assetのwork_idの更新
    for asset_id in assets_id:
        asset_orm = db.query(models.Asset).get(asset_id)
        if asset_orm is None:
            raise HTTPException(status_code=400, detail='This asset id is invalid.')
        asset_orm.work_id = work_orm.id

    # url_infoテーブルへのインスタンスの作成
    for url in urls:
        create_url_info(db, url.get('url'), url.get('url_type', 'other'), work_orm.id, user_id)

    # tagの中間テーブルへのインスタンスの作成
    for tag_id in tags_id:
        tagging_orm = models.Tagging(
            work_id=work_orm.id,
            tag_id=tag_id
        )
        db.add(tagging_orm)
        db.commit()

    # Thumbnailの中間テーブルへのインスタンスの作成
    if thumbnail_asset_id:
        thumbnail = db.query(models.Asset).get(thumbnail_asset_id)
        if thumbnail is None:
            raise HTTPException(status_code=400, detail='This thumbnail asset id is invalid.')
        thumbnail_orm = models.Thumbnail(
            work_id = work_orm.id,
            asset_id = thumbnail.id
        )
        db.add(thumbnail_orm)
        db.commit()

    # schemaに変換
    db.refresh(work_orm)
    work = Work.from_orm(work_orm)

    return work

def get_works_by_limit(db: Session, limit: int, visibility: models.Visibility, oldest_id: str, tags: str, auth: bool = False) -> List[Work]:
    works_orm = db.query(models.Work).order_by(desc(models.Work.created_at)).filter(models.Work.visibility != models.Visibility.draft)
    if tags:
        tag_list = tags.split(',')
        works_orm = works_orm.filter(models.Tagging.tag_id.in_(tag_list)).filter(models.Tagging.work_id == models.Work.id)
        works_orm = works_orm.group_by(models.Work.id).having(func.count(models.Work.id) == len(tag_list))
    if oldest_id:
        limit_work = db.query(models.Work).filter(models.Work.id == oldest_id).first()
        if limit_work is None:
            raise HTTPException(status_code=400, detail='this oldest_id is invalid')
        limit_created_at = limit_work.created_at
        works_orm = works_orm.filter(models.Work.created_at > limit_created_at)
    if not auth:
        works_orm = works_orm.filter(
            models.Work.visibility == models.Visibility.public)
    elif visibility is not None:
        works_orm = works_orm.filter(models.Work.visibility == visibility)
    works_orm = works_orm.limit(limit)
    works_orm = works_orm.all()
    works = list(map(Work.from_orm, works_orm))
    return works

def get_work_by_id(db: Session, work_id: str, user_id: Optional[str]) -> Work:
    work_orm = db.query(models.Work).get(work_id)
    if (work_orm is None) or (work_orm.visibility == models.Visibility.draft and user_id != work_orm.user_id):
        raise HTTPException(status_code=404, detail='work is not found')
    if work_orm.visibility == models.Visibility.private and user_id is None:
        raise HTTPException(status_code=403, detail="This work is a private work. You need to sign in.")
    work = Work.from_orm(work_orm)
    return work

def replace_work(db: Session, work_id: str, title: str, description: str, user_id: str, 
                 visibility: str, thumbnail_asset_id: str, assets_id: List[str],
                 urls: List[BaseUrlInfo], tags_id: List[str]) -> Work:

    work_orm = db.query(models.Work).get(work_id)

    # 自分のWorkでなければ弾く
    if work_orm.user_id != user_id:
        raise HTTPException(status_code=401, detail='this work\'s author isn\'t you')

    # titleのvalidator
    if title == '':
        raise HTTPException(status_code=400, detail="Title is empty")

    # DB更新
    md = markdown.Markdown(extensions=['tables'])
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
    old_thumbnail_orm = db.query(models.Thumbnail).filter(models.Thumbnail.work_id == work_id).first()
    if old_thumbnail_orm:
        old_asset_ids.append(old_thumbnail_orm.asset_id)
    new_asset_ids = assets_id[:]
    if thumbnail_asset_id:
        new_asset_ids.append(thumbnail_asset_id)
    delete_asset_ids = set(old_asset_ids) - set(new_asset_ids)
    for delete_asset_id in delete_asset_ids:
        delete_asset_by_id(db, delete_asset_id, user_id)

    # assetのwork_idの更新
    for asset_id in assets_id:
        asset_orm = db.query(models.Asset).get(asset_id)
        if asset_orm is None:
            raise HTTPException(status_code=400, detail='This asset id is invalid.')
        asset_orm.work_id = work_id

    # url_infoの削除
    urls_orm = db.query(models.UrlInfo).filter(models.UrlInfo.work_id == work_id).all()
    for url_orm in urls_orm:
        delete_url_info(db, url_orm.id)

    # url_infoテーブルへのインスタンスの作成
    for url in urls:
        create_url_info(db, url.get('url'), url.get('url_type', 'other'), work_id, user_id)

    # tagの中間テーブルのインスタンスの削除
    taggings_orm = db.query(models.Tagging).filter(models.Tagging.work_id == work_id).all()
    for tagging in taggings_orm:
        db.delete(tagging)
    db.commit()

    # tagの中間テーブルへのインスタンスの作成
    for tag_id in tags_id:
            tagging_orm = models.Tagging(
                work_id=work_id,
                tag_id=tag_id
            )
            db.add(tagging_orm)
            db.commit()

    # Thumbnailの中間テーブルへのインスタンスの作成
    if thumbnail_asset_id:
        if old_thumbnail_orm:
            db.delete(old_thumbnail_orm)
            db.commit()
        thumbnail = db.query(models.Asset).get(thumbnail_asset_id)
        if thumbnail is None:
            raise HTTPException(status_code=400, detail='This thumbnail asset id is invalid.')
        new_thumbnail_orm = models.Thumbnail(
            work_id = work_id,
            asset_id = thumbnail_asset_id
        )
        db.add(new_thumbnail_orm)
        db.commit()

    # schemaに変換
    db.refresh(work_orm)
    work = Work.from_orm(work_orm)

    return work


def delete_work_by_id(db: Session, work_id: str, user_id: str) -> DeleteStatus:
    work_orm = db.query(models.Work).get(work_id)
    if work_orm.user_id != user_id:
        raise HTTPException(status_code=403, detail='cannot delete other\'s work')

    assets_orm = db.query(models.Asset).filter(models.Asset.work_id == work_id).all()
    urls_orm = db.query(models.UrlInfo).filter(models.UrlInfo.work_id == work_id).all()
    thumbnail_orm = db.query(models.Thumbnail).filter(models.Thumbnail.work_id == work_id).first()

    for asset_orm in assets_orm:
        delete_asset_by_id(db, asset_orm.id, user_id)
        if asset_orm.id == thumbnail_orm.asset_id:
            thumbnail_orm = None

    for url_orm in urls_orm:
        delete_url_info(db, url_orm.id)

    if thumbnail_orm is not None:
        delete_asset_by_id(db, thumbnail_orm.asset_id, user_id)

    db.delete(work_orm)
    db.commit()

    return {'status': 'OK'}

def get_works_by_user_id(db: Session, user_id: str, visiblity:models.Visibility, oldest_id: str, limit: int, tags: str, at_me: bool = False, auth: bool = False) -> List[Work]:
    user_orm = db.query(models.User).get(user_id)
    if user_orm is None:
        raise HTTPException(status_code=404, detail='this user is not exist')

    works_orm = db.query(models.Work).order_by(desc(models.Work.created_at)).filter(models.Work.user_id == user_id)

    if tags:
        tag_list = tags.split(',')
        works_orm = works_orm.filter(models.Tagging.tag_id.in_(
            tag_list)).filter(models.Tagging.work_id == models.Work.id)
        works_orm = works_orm.group_by(models.Work.id).having(func.count(models.Work.id) == len(tag_list))
    if not at_me:
        if auth:
            works_orm = works_orm.filter(models.Work.visibility != models.Visibility.draft)
        else:
            works_orm = works_orm.filter(models.Work.visibility == models.Visibility.public)
        
    if visiblity is not None:
        works_orm = works_orm.filter(models.Work.visibility == visiblity)
    
    if oldest_id:
        limit_work = db.query(models.Work).filter(
            models.Work.id == oldest_id).first()
        if limit_work is None:
            raise HTTPException(
                status_code=400, detail='this oldest_id is invalid')
        limit_created_at = limit_work.created_at
        works_orm = works_orm.filter(models.Work.created_at > limit_created_at)

    works_orm = works_orm.limit(limit)
    works_orm = works_orm.all()
    works = list(map(Work.from_orm, works_orm))
    return works
