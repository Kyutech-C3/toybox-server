from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.datastructures import UploadFile
from fastapi.param_functions import Depends, File, Form
from sqlalchemy.orm.session import Session
from cruds.assets import create_asset, delete_asset_by_id
from cruds.users.auth import GetCurrentUser
from db import get_db
from db.models import AssetType
from schemas.asset import Asset
from schemas.user import User
from schemas.common import DeleteStatus

asset_router = APIRouter()


@asset_router.post("", response_model=Asset)
async def post_asset(
    file: UploadFile = File(...),
    asset_type: AssetType = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    if file is None:
        raise HTTPException(status_code=400, detail="UploadFile is not found")
    created_asset = create_asset(db, user.id, asset_type, file)
    return created_asset


@asset_router.delete("/{asset_id}", response_model=DeleteStatus)
async def delete_asset(
    asset_id: str, db: Session = Depends(get_db), user: User = Depends(GetCurrentUser())
):
    result = delete_asset_by_id(db, asset_id, user.id)
    return result
