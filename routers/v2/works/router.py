from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from cruds.users.auth import GetCurrentUser
from cruds.works.works import get_works_by_pagination
from db import get_db, models
from schemas.user import User
from schemas.work import ResWorks

work_router = APIRouter()


@work_router.get("", response_model=ResWorks)
async def get_works(
    page: int = 1,
    limit: int = 30,
    visibility: models.Visibility = None,
    tag_names: str = None,
    tag_ids: str = None,
    search_word: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser(auto_error=False)),
):
    works = get_works_by_pagination(
        db, limit, visibility, page, tag_names, tag_ids, user, search_word
    )
    return works
