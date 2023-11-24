from fastapi import APIRouter, HTTPException
from fastapi.datastructures import UploadFile
from fastapi.param_functions import Depends, File, Form
from sqlalchemy.orm.session import Session

from blogs.cruds.assets import create_asset
from blogs.schemas import BlogAsset
from cruds.users import GetCurrentUser
from db import BlogAssetType, get_db
from schemas.user import User

asset_router = APIRouter()


@asset_router.post("", response_model=BlogAsset)
async def post_asset(
    file: UploadFile = File(...),
    asset_type: BlogAssetType = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(GetCurrentUser()),
):
    if file is None:
        raise HTTPException(status_code=400, detail="upload_file is not found")
    filename = file.filename
    if filename is None:
        raise HTTPException(
            status_code=400, detail="upload_file's filename is not found"
        )
    created_asset = create_asset(
        db, user.id, asset_type, file, filename[filename.rfind(".") + 1 :]
    )
    return created_asset
