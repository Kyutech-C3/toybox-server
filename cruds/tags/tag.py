from typing import List
from fastapi import HTTPException
from db import models
from sqlalchemy.orm.session import Session
from schemas.tag import Tag

def create_tag(db: Session, name: str, color_code: str, community_id: str) -> Tag:
    if name == '':
        raise HTTPException(status_code=400, detail="Name is empty")

    result_by_name_and_community_id = db.query(models.Tag).filter(models.Tag.community_id == community_id, models.Tag.name == name).first()
    if result_by_name_and_community_id != None:
        raise HTTPException(
            status_code=400,
            detail="The tag is exist"
        )
    
    result_by_community_id = db.query(models.Community).filter(models.Community.id == community_id).first()
    if result_by_community_id is None:
        raise HTTPException(
            status_code=400,
            detail="The community is not exist"
        )

    tag_orm = models.Tag(
        name=name,
        community_id=community_id,
        color=color_code
    )
    db.add(tag_orm)
    db.commit()
    db.refresh(tag_orm)

    print(tag_orm.name)
    print(tag_orm.community_id)
    print(tag_orm.color)

    tag = Tag.from_orm(tag_orm)

    return tag

def get_tags_all(db: Session, limit: int, offset_id: str) -> List[Tag]:
    tag_orm = db.query(models.Tag)
    if tag_orm is None:
        raise HTTPException(
            status_code=400,
            detail="Tags is not exist"
        )
    if offset_id:
        limit_work = db.query(models.Tag).filter(models.Tag.id == offset_id).first()
        if limit_work is None:
            raise HTTPException(
                status_code=400,
                detail="offset_id is not exist"
            )
        limit_created_at = limit_work.created_at
        tag_orm = tag_orm.filter(models.Tag.created_at > limit_created_at)
    tag_orm = tag_orm.limit(limit)
    tag_orm = tag_orm.all()
    tag_list = list(map(Tag.from_orm, tag_orm))
    
    return tag_list

def get_tags_by_community_id(db: Session, limit: int, offset_id: str, community_id: str) -> List[Tag]:
    tag_orm = db.query(models.Tag).filter(models.Tag.community_id == community_id)
    if offset_id:
        limit_work = db.query(models.Tag).filter(models.Tag.id == offset_id).first()
        if limit_work is None:
            raise HTTPException(
                status_code=400,
                detail="offset_id is not exist"
            )
        limit_created_at = limit_work.created_at
        tag_orm = tag_orm.filter(models.Tag.created_at > limit_created_at)
    tag_orm = tag_orm.limit(limit)
    tag_orm = tag_orm.all()
    tag_list = list(map(Tag.from_orm, tag_orm))
    
    return tag_list

def get_tag_by_id(db: Session, tag_id: str) -> Tag:
    tag_orm = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if tag_orm is None:
        raise HTTPException(
            status_code=400,
            detail="The tag specified by id is not exist"
        )
    tag = Tag.from_orm(tag_orm)
    return tag

def change_tag_by_id(db: Session, name: str, community_id: str, color: str, tag_id: str) -> Tag:
    tag_orm = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if tag_orm is None:
        raise HTTPException(
            status_code=400,
            detail="The tag specified by id is not exist"
        )
    tag_orm.name = tag_orm.name if name is None else name
    if community_id != None:
        result_by_community_id = db.query(models.Community).filter(models.Community.id == community_id).first()
        if result_by_community_id is None:
            raise HTTPException(
                status_code=400,
                detail="The community is not exist"
            )
        tag_orm.community_id = community_id
    tag_orm.color = tag_orm.color if color is None else color

    db.commit()
    db.refresh(tag_orm)
    tag = Tag.from_orm(tag_orm)
    return tag

def delete_tag_by_id(db: Session, tag_id: str) -> str:
    tag_orm = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if tag_orm == None:
        raise HTTPException(
            status_code=400,
            detail="The tag is not exist"
        )
    
    db.delete(tag_orm)
    db.commit()

    return "OK"
