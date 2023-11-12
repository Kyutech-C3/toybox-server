import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import router

# from routers.v2.router import v2
from utils.limit_upload_size import LimitUploadSize

app = FastAPI(title="toybox-server")

app.add_middleware(LimitUploadSize, max_upload_size=2_147_483_648)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOW_ORIGIN_URLS").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
# TODO: v2の実装
# app.include_router(v2, prefix="/api/v2",tags=["v2"])
