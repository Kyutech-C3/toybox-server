from sqlalchemy.orm.session import Session
from db import models

from schemas.url_info import UrlInfo

def create_url_info(db: Session, url: str, url_type: str, work_id: str, user_id: str):
    url_info_orm = models.UrlInfo(
        work_id = work_id,
        url = url,
        url_type = url_type,
        user_id = user_id
    )

    db.add(url_info_orm)
    db.commit()
    db.refresh(url_info_orm)