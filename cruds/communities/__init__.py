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