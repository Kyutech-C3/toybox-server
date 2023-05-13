from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import router
from utils.limit_upload_size import LimitUploadSize

import os

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
