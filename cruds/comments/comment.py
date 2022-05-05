from fastapi import HTTPException
from db import models
from sqlalchemy.orm.session import Session
from schemas.comment import ResponseComment

def create_comment(db: Session, content: str, work_id: str, user_id: str = None, reply_at: str = None, scope: str = None) -> ResponseComment:
    if reply_at:
        comment_orm = db.query(models.Comment).filter(models.Comment.id == reply_at).first()
        if comment_orm is None:
            raise HTTPException(
                status_code=400,
                detail="reply_at is invalid"
            )
        
        if comment_orm.reply_at:
            raise HTTPException(
                status_code=400,
                detail="Can't reply to this reply_at"
            )

        comment_orm.number_of_reply += 1
        db.commit()

    scope_volume: str = None
    
    if scope:
        scope_volume = user_id

    
    comment_orm = models.Comment(
        content = content,
        work_id = work_id,
        user_id = user_id,
        reply_at = reply_at,
        number_of_reply = 0,
        scope = scope_volume
    )

    db.add(comment_orm)
    db.commit()
    db.refresh(comment_orm)

    comment = ResponseComment.from_orm(comment_orm)

    return comment

def get_comments_by_work_id(db: Session, limit: int = 30, offset_id: str = None, work_id: str = None, auth: bool = False) -> list[ResponseComment]:
    work_orm = db.query(models.Work).filter(models.Work.id == work_id).first()
    if work_orm is None:
        raise HTTPException(
            status_code=400,
            detail="work_id is invalid"
        )
    
    comments_orm = db.query(models.Comment).filter(models.Comment.work_id == work_id).filter(models.Comment.reply_at == None)
    if comments_orm is None:
        raise HTTPException(
            status_code=400,
            detail="Comments is not exist"
        )
    
    if not auth:
        comments_orm = comments_orm.filter(models.Comment.scope == None)
        if comments_orm is None:
            raise HTTPException(
                status_code=400,
                detail="Public comments is not exist"
            )

    if offset_id:
        offset = db.query(models.Comment).filter(models.Comment.id == offset_id).first()
        if offset is None:
            raise HTTPException(
                status_code=400,
                detail="offset_id is invalid"
            )
        offset_created_at = offset.created_at
        comments_orm = comments_orm.filter(models.Comment.created_at > offset_created_at)
    comments_orm = comments_orm.limit(limit)
    comments_orm = comments_orm.all()
    comments = list(map(ResponseComment.from_orm, comments_orm))
    
    return comments

def get_reply_comments_by_comment_id(db: Session, comment_id: str, limit: int = 30, offset_id: str = None, auth: bool = False) -> list[ResponseComment]:
    comment_orm = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment_orm is None:
        raise HTTPException(
            status_code=400,
            detail="comment_id is invalid"
        )
    
    comments_orm = db.query(models.Comment).filter(models.Comment.reply_at == comment_id)
    if comments_orm is None:
        raise HTTPException(
            status_code=400,
            detail="Comments is not exist"
        )

    if not auth:
        comments_orm = comments_orm.filter(models.Comment.scope == None)
        if comments_orm is None:
            raise HTTPException(
                status_code=400,
                detail="Public comments is not exist"
            )

    if offset_id:
        offset = db.query(models.Comment).filter(models.Comment.id == offset_id).first()
        if offset is None:
            raise HTTPException(
                status_code=400,
                detail="offset_id is invalid"
            )
        offset_created_at = offset.created_at
        comments_orm = comments_orm.filter(models.Comment.created_at > offset_created_at)
    comments_orm = comments_orm.limit(limit)
    comments_orm = comments_orm.all()
    comments = list(map(ResponseComment.from_orm, comments_orm))
    
    return comments

def delete_by_comment_id(db: Session, comment_id: str = None, user_id: str = None) -> str:
    if user_id is None:
        raise HTTPException(
            status_code=400,
            detail="user_id is not specified"
        )
    comment_orm = db.query(models.Comment)
    comment = comment_orm.filter(models.Comment.id == comment_id).first()
    if comment == None:
        raise HTTPException(
            status_code=400,
            detail="Comment is not exist"
        )

    comment_orm = comment_orm.filter(models.Comment.id == comment_id).filter(models.Comment.user_id == user_id).first()
    if comment_orm == None:
        raise HTTPException(
                status_code=400,
                detail="User id is invalid"
            )

    db.delete(comment_orm)
    db.commit()

    result = "OK"

    return result