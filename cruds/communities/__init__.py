from sqlalchemy.sql.functions import mode
from routers import communities
from db import models
from schemas.community import Community
from sqlalchemy.orm.session import Session
import markdown
from fastapi import HTTPException
from typing import List

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

def get_community_list(db: Session, limit: int = 30, oldest_id: str = None) -> List[Community]: 
    community_list_orm = db.query(models.Community).order_by(models.Community.created_at)
    if oldest_id:
        limit_community = db.query(models.Community).filter(models.Community.id == oldest_id).first()
        if limit_community is None:
            raise HTTPException(status_code=400, detail="oldest_id is wrong")
        limit_community_created_at = limit_community.created_at
        community_list_orm = community_list_orm.filter(models.Community.created_at > limit_community_created_at)
    community_list_orm = community_list_orm.limit(limit)
    community_list_orm = community_list_orm.all()
    community_list = list(map(Community.from_orm, community_list_orm))
    return community_list

def get_community_by_id(db: Session, community_id: str) -> Community:
    community_orm = db.query(models.Community).get(community_id)
    if community_orm is None:
        raise HTTPException(status_code=404, detail="community isn't found")
    community = Community.from_orm(community_orm)
    return community

def put_community_by_id(db: Session, name: str, description: str, community_id: str) -> Community:
    if len(name) <= 0:
        raise HTTPException(status_code=400, detail="Community name is empty")
    put_community_orm = db.query(models.Community).filter(models.Community.id == community_id).first()
    if put_community_orm is None:
        raise HTTPException(status_code=400, detail="community_id is wrong")
    put_community_orm.name = name
    put_community_orm.description = description
    db.commit()

    community_put = Community.from_orm(put_community_orm)
    return community_put

def delete_community_by_id(db: Session, community_id: str):
    delete_community = db.query(models.Community).filter(models.Community.id==community_id).first()
    if delete_community is None:
        raise HTTPException(status_code=400, detail="community_id is wrong")
    db.delete(delete_community)
    db.commit()

    