from sqlalchemy.sql.functions import mode
from routers import communities
from db import models
from schemas.community import Community
from sqlalchemy.orm.session import Session
import markdown
from fastapi import HTTPException

def create_community(db: Session, name: str, description: str) -> Community:
    if len(name) <= 0:
        raise HTTPException(status_code=400, detail="Community name is empty")

    md = markdown.Markdown(extensions=['tables'])
    community_orm = models.Community(
        name=name,
        description=description,
        description_html=md.convert(description)
    )
    db.add(community_orm)
    db.commit()
    db.refresh(community_orm)

    community = Community.from_orm(community_orm)
    return community

def get_community_by_limit(db: Session, limit: int, oldest_id: str):
    community_list_orm = db.query(models.Community).order_by(models.Community.created_at)
    if oldest_id:
        limit_community = db.query(models.Community).filter(models.Community.id == oldest_id).first()
        if limit_community is None:
            raise HTTPException(status_code=400, detail="oldest_id is wrong")
        limit_community_at = limit_community.created_at
        community_list_orm = community_list_orm.filter(models.Community.created_at > limit_community_at)
    community_list_orm = community_list_orm.limit(limit)
    community_list_orm = community_list_orm.all()
    community_list = list(map(Community.from_orm, community_list_orm))
    return community_list

def get_community_by_id(db: Session, community_id: str) -> Community:
    community_orm = db.query(models.Community).get(community_id)
    community = Community.from_orm(community_orm)
    return community