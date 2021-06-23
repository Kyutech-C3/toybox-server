from fastapi import APIRouter
from .users import user_router
from .works import work_router
from .assets import asset_router

router = APIRouter()

router.include_router(user_router, prefix='/users', tags=['users'])
router.include_router(work_router, prefix='/works', tags=['works'])
router.include_router(asset_router, prefix='/assets', tags=['assets'])