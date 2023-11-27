from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from blogs.db import models as blog_models
from blogs.schemas import BlogAsset
from utils.wasabi import ALLOW_EXTENSIONS, upload_asset


def create_asset(
    db: Session, user_id: str, asset_type: str, file: UploadFile, extension: str
) -> BlogAsset:
    extension = extension.lower()
    if extension not in ALLOW_EXTENSIONS.get(asset_type, []):
        raise HTTPException(status_code=400, detail="this file extension is invalid")

    asset_orm = blog_models.BlogAsset(
        asset_type=asset_type, user_id=user_id, extension=extension
    )
    db.add(asset_orm)
    db.commit()
    db.refresh(asset_orm)

    file_url = upload_asset(asset_orm.id, file.file, extension)
    if file_url is None:
        raise HTTPException(status_code=500, detail="file upload failed")

    asset = BlogAsset.from_orm(asset_orm)
    asset.url = file_url

    return asset
