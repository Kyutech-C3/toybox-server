from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from routers import router
from db import engine
from db.models import Base
from fastapi.staticfiles import StaticFiles
import os

Base.metadata.create_all(engine)
app = FastAPI(
    title='toybox-server'
)

upload_folder = os.environ.get('UPLOAD_FOLDER')

app.mount("/static", StaticFiles(directory=upload_folder), name="static")

origins = [
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

app.include_router(router, prefix='/api/v1')