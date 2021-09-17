from typing import List
from fastapi import HTTPException
from db import models
from sqlalchemy.orm.session import Session
from schemas.work import Work
import markdown

def create_work(db: Session, title: str, description: str, work_url: str, github_url: str, user_id: str, community_id: str, private: bool) -> Work:
    if title == '':
        raise HTTPException(status_code=400, detail="Title is empty")

    md = markdown.Markdown(extensions=['tables'])
    work_orm = models.Work(
        title=title,
        description=description,
        description_html=md.convert(description),
        user_id=user_id,
        community_id=community_id,
        work_url=work_url,
        github_url=github_url,
        private=private
    )
    db.add(work_orm)
    db.commit()
    db.refresh(work_orm)

    print(work_orm.user_id)
    print(work_orm.community_id)

    work = Work.from_orm(work_orm)

    return work

def get_work_by_id(db: Session, work_id: str) -> Work:
    work_orm = db.query(models.Work).get(work_id)
    if work_orm == None:
        return None
    return Work.from_orm(work_orm)

def get_works_by_limit(db: Session, limit: int, oldest_id: str, private: bool = False) -> List[Work]:
    works_orm = db.query(models.Work).order_by(models.Work.created_at)
    if oldest_id:
        limit_work = db.query(models.Work).filter(models.Work.id == oldest_id).first()
        limit_created_at = limit_work.created_at
        works_orm = works_orm.filter(models.Work.created_at > limit_created_at)
    if not private:
        works_orm = works_orm.filter(models.Work.private == False)
    works_orm = works_orm.limit(limit)
    works_orm = works_orm.all()
    works = list(map(Work.from_orm, works_orm))
    return works

def get_work_by_id(db: Session, work_id: str, private: bool = False) -> Work:
    work_orm = db.query(models.Work).get(work_id)
    work = Work.from_orm(work_orm)
    if work.private and not private:
        raise HTTPException(status_code=403, detail="This work is a private work. You need to sign in.")
    return work
