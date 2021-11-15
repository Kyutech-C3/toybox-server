from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from db import models
import re

url_type_pattern = {
    'youtube': '^https://(www\.youtube\.com/watch\?v=|youtu\.be/)[\S]{11}$',
    'soundcloud': '^https://soundcloud\.com/[^/]+/[^/]+$',
    'github': '^https://github\.com/[^/]+/[^/]+$',
    'sketchfab': '^https://sketchfab\.com/3d-models/[\w]+-[\da-z]{32}$',
    'unityroom': '^https://unityroom\.com/games/[\S]+$',
    'other': '^https?://[\w/:%#\$&\?\(\)~\.=\+-]+$',
    'default': '^.'
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
    db.refresh(url_info_orm)

def delete_url_info(db: Session, url_info_id: str):
    url_info_orm = db.query(models.UrlInfo).get(url_info_id)
    if url_info_orm is None:
        raise HTTPException(status_code=400, detail='this url_info is not exist')
    db.delete(url_info_orm)
    db.commit()