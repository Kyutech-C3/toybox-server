from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from blogs.db import models as blog_models
from blogs.schemas import Asset
from utils.wasabi import ALLOW_EXTENSIONS, BLOG_S3_DIR, REGION_NAME, S3_BUCKET, wasabi


def create_asset(
    db: Session, user_id: str, asset_type: str, file: UploadFile, extension: str
) -> Asset:
    extension = extension.lower()
    if extension not in ALLOW_EXTENSIONS.get(asset_type, []):
        raise HTTPException(status_code=400, detail="this file extension is invalid")

    asset_orm = blog_models.BlogAsset(
        asset_type=asset_type, user_id=user_id, extension=extension
    )
    db.add(asset_orm)
    db.commit()
    db.refresh(asset_orm)

    key = f"{BLOG_S3_DIR}_blog/{asset_type}/{asset_orm.id}/origin.{extension}"
    wasabi.put_object(
        Body=file.file,
        Bucket=S3_BUCKET,
        Key=key,
    )

    db.commit()
    db.refresh(asset_orm)

    asset = Asset.from_orm(asset_orm)
    asset.url = f"https://s3.{REGION_NAME}.wasabisys.com/{S3_BUCKET}/{key}"

    return asset
