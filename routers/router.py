from fastapi import APIRouter

from .assets import asset_router
from .auth import auth_router
from .comments import comment_router
from .favorites import favorite_router, user_favorite_router
from .tags import tag_router
from .users import user_router
from .works import work_router

router = APIRouter()

work_router.include_router(comment_router)
work_router.include_router(favorite_router)
user_router.include_router(user_favorite_router)
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(user_router, prefix="/users", tags=["users"])
router.include_router(tag_router, prefix="/tags", tags=["tags"])
router.include_router(work_router, prefix="/works", tags=["works"])
router.include_router(asset_router, prefix="/assets", tags=["assets"])
