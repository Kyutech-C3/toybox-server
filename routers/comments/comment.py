from schemas.comment import PostComment, ResponseComment, ResponseReplyComment
from schemas.user import User
from schemas.common import DeleteStatus
from fastapi import APIRouter
from db import get_db, models
from fastapi.params import Depends
from sqlalchemy.orm import Session
from cruds.users.auth import GetCurrentUser
from cruds.comments.comment import create_comment, get_comments_by_work_id, get_reply_comments_by_comment_id, delete_by_comment_id

comment_router = APIRouter()

@comment_router.post('/{work_id}/comments', response_model=ResponseComment)
async def post_comment(payload: PostComment, work_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser(auto_error=False)), reply_at: str = None, visibility: models.Visibility = 'public'):
  try:
    user_id = user.id
  except AttributeError:
    user_id = None
  comment = create_comment(db, payload.content, work_id, user_id, reply_at, visibility)
  return comment

@comment_router.get('/{work_id}/comments', response_model=list[ResponseComment])
async def get_comments(work_id: str, db: Session = Depends(get_db), limit: int = 30, offset_id: str = None, user: User = Depends(GetCurrentUser(auto_error=False))):
  auth = user is not None
  comments = get_comments_by_work_id(work_id, db, limit, offset_id, auth)
  return comments

@comment_router.get('/{work_id}/comments/{comment_id}', response_model=list[ResponseReplyComment])
async def get_reply_comments(work_id: str, comment_id: str, db: Session = Depends(get_db), limit: int = 10, offset_id: str = None, user: User = Depends(GetCurrentUser(auto_error=False))):
  auth = user is not None
  replies = get_reply_comments_by_comment_id(db, comment_id, work_id, limit, offset_id, auth)
  return replies

@comment_router.delete('/{work_id}/comments/{comment_id}', response_model=DeleteStatus)
async def delete_comment(comment_id: str, work_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
  status = delete_by_comment_id(db, comment_id, work_id, user.id)
  return status
