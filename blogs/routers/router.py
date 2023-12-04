from fastapi import APIRouter

from .assets import asset_router
from .blogs import blog_router, users_blog_router
from .favorites import favorite_router

router = APIRouter()

blog_router.include_router(favorite_router)
router.include_router(blog_router, prefix="/blogs", tags=["blogs"])
router.include_router(asset_router, prefix="/blogs/assets", tags=["assets"])
router.include_router(users_blog_router, prefix="/users", tags=["blogs"])
