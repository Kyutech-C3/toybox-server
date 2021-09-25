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

def get_tag(db: Session, tag_id: str) -> Tag:
    result_by_id = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if result_by_id == None:
        raise HTTPException(
            status_code=400,
            detail="The tag specified by id is not exist"
        )
    tag = Tag.from_orm(result_by_id)
    return tag
