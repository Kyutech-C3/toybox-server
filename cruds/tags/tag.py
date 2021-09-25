from fastapi import HTTPException
from db import models
from sqlalchemy.orm.session import Session
from schemas.tag import Tag

def create_tag(db: Session, name: str, color_code: str, community_id: str) -> Tag:
    if name == '':
        raise HTTPException(status_code=400, detail="Name is empty")

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