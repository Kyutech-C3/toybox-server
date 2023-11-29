from fastapi import APIRouter
from routers.v2.works.router import work_router

v2_router = APIRouter()

v2_router.include_router(work_router, prefix="/works", tags=["works"])
