from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from db import models
from schemas.asset import Asset
from schemas.common import DeleteStatus
from utils.wasabi import ALLOW_EXTENSIONS, remove_asset, upload_asset


def create_asset(
    db: Session, user_id: str, asset_type: str, file: UploadFile, extension: str
) -> Asset:
    extension = extension.lower()
    if extension not in ALLOW_EXTENSIONS.get(asset_type, []):
        raise HTTPException(status_code=400, detail="this file extension is invalid")

    asset_orm = models.Asset(
        asset_type=asset_type, user_id=user_id, extension=extension, url=""
    )
    db.add(asset_orm)
    db.commit()
    db.refresh(asset_orm)

    file_url = upload_asset(asset_orm.id, file.file, extension)
    if file_url is None:
        raise HTTPException(status_code=500, detail="file upload failed")

    asset_orm.url = file_url
    db.commit()
    db.refresh(asset_orm)

    asset = Asset.from_orm(asset_orm)
    return asset


def delete_asset_by_id(db: Session, asset_id: str, user_id: str) -> DeleteStatus:
    asset_orm = db.query(models.Asset).get(asset_id)
    if asset_orm is None:
        raise HTTPException(status_code=404, detail="this asset is not exist")
    if asset_orm.user_id != user_id:
        raise HTTPException(status_code=403, detail="cannot delete other's asset")

    remove_asset(asset_orm.id, asset_orm.asset_type)

    db.delete(asset_orm)
    db.commit()

    return {"status": "OK"}
