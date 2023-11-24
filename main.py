import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import router, v2_router
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
app.include_router(v2_router, prefix="/api/v2", tags=["v2"])
