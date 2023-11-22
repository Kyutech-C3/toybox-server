from fastapi import APIRouter

from .assets import asset_router
from .blogs import blog_router
from .favorites import favorite_router

router = APIRouter(prefix="/blogs")

blog_router.include_router(favorite_router)
router.include_router(blog_router, tags=["blogs"])
router.include_router(asset_router, prefix="/assets", tags=["assets"])
