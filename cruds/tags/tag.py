from typing import List
from fastapi import HTTPException
from db import models
from sqlalchemy.orm.session import Session
from schemas.tag import PostTag, GetTag, BaseTag, TagResponsStatus

def create_tag(db: Session, name: str, color_code: str) -> GetTag:
    if name == '':
        raise HTTPException(status_code=400, detail="Name is empty")

    result_by_name = db.query(models.Tag).filter(models.Tag.name == name).first()
    if result_by_name != None:
        raise HTTPException(
            status_code=400,
            detail="The tag is exist"
        )
    

    tag_orm = models.Tag(
        name=name,
        color=color_code
    )
    db.add(tag_orm)
    db.commit()
    db.refresh(tag_orm)

    print(tag_orm.name)
    print(tag_orm.color)

    tag = GetTag.from_orm(tag_orm)

    return tag

def get_tags(db: Session, limit: int = 30, offset_id: str = None) -> List[GetTag]:
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
    tag_list = list(map(GetTag.from_orm, tag_orm))
    
    return tag_list

def get_tag_by_id(db: Session, tag_id: str) -> GetTag:
    tag_orm = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if tag_orm is None:
        raise HTTPException(
            status_code=404,
            detail="The tag specified by id is not exist"
        )
    tag = GetTag.from_orm(tag_orm)
    return tag

def change_tag_by_id(db: Session, name: str, color: str, tag_id: str) -> GetTag:
    tag_orm = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if tag_orm is None:
        raise HTTPException(
            status_code=400,
            detail="The tag specified by id is not exist"
        )
    tag_orm.name = tag_orm.name if name is None else name
    tag_orm.color = tag_orm.color if color is None else color

    db.commit()
    db.refresh(tag_orm)
    tag = GetTag.from_orm(tag_orm)
    return tag

def delete_tag_by_id(db: Session, tag_id: str) -> TagResponsStatus:
    tag_orm = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if tag_orm == None:
        raise HTTPException(
            status_code=400,
            detail="The tag is not exist"
        )
    
    db.delete(tag_orm)
    db.commit()

    result = TagResponsStatus(status="OK")

    return result
