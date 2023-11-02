from typing import List

from fastapi import HTTPException
from sqlalchemy.orm.session import Session

from db import models
from schemas.tag import GetTag, TagResponsStatus


def create_tag(db: Session, name: str, color_code: str) -> GetTag:
    if name == "":
        raise HTTPException(status_code=400, detail="Name is empty")

    result_by_name = db.query(models.Tag).filter(models.Tag.name == name).first()
    if result_by_name is not None:
        raise HTTPException(status_code=400, detail="The tag is exist")

    tag_orm = models.Tag(name=name, color=color_code)
    db.add(tag_orm)
    db.commit()
    db.refresh(tag_orm)

    print(tag_orm.name)
    print(tag_orm.color)

    tag = GetTag.from_orm(tag_orm)

    return tag


def get_tags(
    db: Session, limit: int, smallest_tag_id: str, biggest_tag_id: str, search_str: str
) -> List[GetTag]:
    tag_orm = db.query(models.Tag).order_by(models.Tag.name)
    if tag_orm.first() is None:
        return []

    if search_str is not None:
        tag_orm = tag_orm.filter(models.Tag.name.ilike(f"{search_str}%"))

    if smallest_tag_id:
        limit_tag = (
            db.query(models.Tag).filter(models.Tag.id == smallest_tag_id).first()
        )
        if limit_tag is None:
            raise HTTPException(status_code=400, detail="smallest_tag is not exist")
        tag_orm = tag_orm.filter(models.Tag.name > smallest_tag_id.name)
    if biggest_tag_id:
        limit_tag = db.query(models.Tag).filter(models.Tag.id == biggest_tag_id).first()
        if limit_tag is None:
            raise HTTPException(status_code=400, detail="biggest_tag is not exist")
        tag_orm = tag_orm.filter(models.Tag.name > biggest_tag_id.name)

    tag_orm = tag_orm.limit(limit).all()
    tag_list = list(map(GetTag.from_orm, tag_orm))

    return tag_list


def get_tag_by_id(db: Session, tag_id: str) -> GetTag:
    tag_orm = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if tag_orm is None:
        raise HTTPException(
            status_code=404, detail="The tag specified by id is not exist"
        )
    tag = GetTag.from_orm(tag_orm)
    return tag


def change_tag_by_id(db: Session, name: str, color: str, tag_id: str) -> GetTag:
    tag_orm = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if tag_orm is None:
        raise HTTPException(
            status_code=400, detail="The tag specified by id is not exist"
        )
    tag_orm.name = tag_orm.name if name is None else name
    tag_orm.color = tag_orm.color if color is None else color

    db.commit()
    db.refresh(tag_orm)
    tag = GetTag.from_orm(tag_orm)
    return tag


def delete_tag_by_id(db: Session, tag_id: str) -> TagResponsStatus:
    tag_orm = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if tag_orm is None:
        raise HTTPException(status_code=400, detail="The tag is not exist")

    db.delete(tag_orm)
    db.commit()

    result = TagResponsStatus(status="OK")

    return result
