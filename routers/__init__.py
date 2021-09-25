from fastapi import APIRouter
from .users import user_router
from .works import work_router
from .tags.tag import tag_router
from .assets import asset_router
from .auth import auth_router
from .communities import community_router

router = APIRouter()

router.include_router(auth_router, prefix='/auth', tags=['auth'])
router.include_router(user_router, prefix='/users', tags=['users'])
router.include_router(tag_router, prefix='/tags', tags=['tags'])
router.include_router(work_router, prefix='/works', tags=['works'])
router.include_router(asset_router, prefix='/assets', tags=['assets'])
router.include_router(community_router, prefix='/communities', tags=['communities'])