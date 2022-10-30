from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from db import models
import re

url_type_pattern = {
    'youtube': r'^https://(www\.youtube\.com/watch\?v=|youtu\.be/)[\S]{11}$',
    'soundcloud': r'^https://soundcloud\.com/[^/]+/[^/]+$',
    'github': r'^https://github\.com/[^/]+/[^/]+$',
    'sketchfab': r'^https://sketchfab\.com/3d-models/[\w]+-[\da-z]{32}$',
    'unityroom': r'^https://unityroom\.com/games/[\S]+$',
    'other': r'^https?://[\w/:%#\$&\?\(\)~\.=\+-]+$'
}

def create_url_info(db: Session, url: str, url_type: str, work_id: str, user_id: str):
    pattern = url_type_pattern.get(url_type, '')
    print(pattern)
    if not re.match(pattern, url):
        raise HTTPException(status_code=400, detail='url pattern is invalid')
    url_info_orm = models.UrlInfo(
        work_id = work_id,
        url = url,
        url_type = url_type,
        user_id = user_id
    )

    db.add(url_info_orm)
    db.commit()

def delete_url_info(db: Session, url_info_id: str):
    url_info_orm = db.query(models.UrlInfo).get(url_info_id)
    if url_info_orm is None:
        raise HTTPException(status_code=400, detail='this url_info is not exist')
    db.delete(url_info_orm)
    db.commit()