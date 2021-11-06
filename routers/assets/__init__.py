from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.datastructures import UploadFile
from fastapi.param_functions import Body, Depends, File, Form
from sqlalchemy.orm.session import Session
from cruds.assets import create_asset
from cruds.users.auth import GetCurrentUser
from db import get_db
from schemas.asset import Asset, BaseAsset
from schemas.user import User

asset_router = APIRouter()

@asset_router.post('', response_model=Asset)
async def post_asset(file: UploadFile = File(...), asset_type: str = Form(...), db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())):
    created_asset = None
    if file is None:
        raise HTTPException(status_code=400, detail='UploadFile is not found')
    created_asset = create_asset(db, user.id, asset_type, file)
    return created_asset