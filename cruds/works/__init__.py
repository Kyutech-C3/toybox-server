from typing import List
from fastapi import HTTPException
from cruds.url_infos import create_url_info
from db import models
from sqlalchemy.orm.session import Session
from schemas.url_info import BaseUrlInfo
from schemas.work import Work
import markdown

def set_work(db: Session, title: str, description: str, user_id: str, 
    community_id: str, visibility: str, thumbnail_asset_id: str, assets_id: List[str], 
    urls: List[BaseUrlInfo]) -> Work:
    
    if title == '':
        raise HTTPException(status_code=400, detail="Title is empty")

    md = markdown.Markdown(extensions=['tables'])
    work_orm = models.Work(
        title = title,
        description = description,
        description_html = md.convert(description),
        user_id = user_id,
        community_id = community_id,
        visibility = visibility,
    )
    db.add(work_orm)
    db.commit()
    db.refresh(work_orm)

    for asset_id in assets_id:
        asset_orm = db.query(models.Asset).get(asset_id)
        if asset_orm is None:
            raise HTTPException(status_code=400, detail='This asset id is invalid.')
        asset_orm.work_id = work_orm.id

    for url in urls:
        create_url_info(db, url.get('url'), url.get('type', 'other'), work_orm.id, user_id)

    thumbnail = db.query(models.Asset).get(thumbnail_asset_id)
    if thumbnail is None:
        raise HTTPException(status_code=400, detail='This thumbnail asset id is invalid.')
    thumbnail_orm = models.Thumbnail(
        work_id = work_orm.id,
        asset_id = thumbnail.id
    )

    db.add(thumbnail_orm)

    db.commit()
    db.refresh(work_orm)

    work = Work.from_orm(work_orm)

    return work

def get_work_by_id(db: Session, work_id: str) -> Work:
    work_orm = db.query(models.Work).get(work_id)
    if work_orm == None:
        return None
    return Work.from_orm(work_orm)

def get_works_by_limit(db: Session, limit: int, oldest_id: str, auth: bool = False) -> List[Work]:
    works_orm = db.query(models.Work).order_by(models.Work.created_at).filter(models.Work.visibility != models.Visibility.draft)
    if oldest_id:
        limit_work = db.query(models.Work).filter(models.Work.id == oldest_id).first()
        limit_created_at = limit_work.created_at
        works_orm = works_orm.filter(models.Work.created_at > limit_created_at)
    if not auth:
        works_orm = works_orm.filter(models.Work.visibility == models.Visibility.public)
    works_orm = works_orm.limit(limit)
    works_orm = works_orm.all()
    works = list(map(Work.from_orm, works_orm))
    return works

def get_work_by_id(db: Session, work_id: str, auth: bool = False) -> Work:
    work_orm = db.query(models.Work).get(work_id)
    if work_orm.visibility == models.Visibility.draft:
        raise HTTPException(status_code=400, detail="This work is a draft work.")
    work = Work.from_orm(work_orm)
    if work.visibility == models.Visibility.private and not auth:
        raise HTTPException(status_code=403, detail="This work is a private work. You need to sign in.")
    return work
