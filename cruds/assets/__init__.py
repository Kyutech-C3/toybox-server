import os, shutil
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from db import models
from schemas.asset import Asset
from schemas.common import DeleteStatus
import boto3

ALLOW_EXTENSIONS = {
    'image': ['png', 'jpg', 'jpeg', 'bmp', 'gif'],
    'video': ['mp4', 'mov', 'avi', 'flv'],
    'music': ['mp3', 'wav', 'm4a'],
    'zip': ['zip'],
    'model': ['gltf', 'fbx']
}

S3_BUCKET = os.environ.get('S3_BUCKET')
S3_DIR = os.environ.get('S3_DIR')
REGION_NAME = os.environ.get('REGION_NAME')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_ACCESS_KEY = os.environ.get('SECRET_ACCESS_KEY')

wasabi = boto3.client("s3", endpoint_url = f"https://s3.{REGION_NAME}.wasabisys.com", aws_access_key_id = ACCESS_KEY, aws_secret_access_key = SECRET_ACCESS_KEY)

def create_asset(db: Session, user_id: str, asset_type: str, file: UploadFile) -> Asset:
    filename = file.filename
    if filename == '':
        raise HTTPException(status_code=400, detail='this file is invalid')
    file_extension = filename[filename.rfind('.')+1:].lower()
    if not file_extension in ALLOW_EXTENSIONS.get(asset_type, []):
        raise HTTPException(status_code=400, detail='this file extension is invalid')

    asset_orm = models.Asset(
        asset_type = asset_type,
        user_id = user_id,
        extension = file_extension,
        url = ''
    )
    db.add(asset_orm)
    db.commit()
    db.refresh(asset_orm)


    response = wasabi.put_object(
        Body = file.file,
        Bucket = S3_BUCKET,
        Key = f"{S3_DIR}/{asset_type}/{asset_orm.id}/origin.{file_extension}"
    )

    file_url = "https://s3.%s.wasabisys.com/%s" % (REGION_NAME, f"{S3_BUCKET}/{S3_DIR}/{asset_type}/{asset_orm.id}/origin.{file_extension}")

    asset_orm.url = file_url
    db.commit()
    db.refresh(asset_orm)

    asset = Asset.from_orm(asset_orm)
    return asset

def delete_asset_by_id(db: Session, asset_id: str, user_id: str) -> DeleteStatus:
    asset_orm = db.query(models.Asset).get(asset_id)
    if asset_orm is None:
        raise HTTPException(status_code=404, detail='this asset is not exist')
    if asset_orm.user_id != user_id:
        raise HTTPException(status_code=403, detail='cannot delete other\'s asset')

    response = wasabi.delete_object(
        Bucket = S3_BUCKET,
        Key = f"{S3_DIR}/{asset_orm.asset_type}/{asset_orm.id}"
    )

    db.delete(asset_orm)
    db.commit()

    return {'status': 'OK'}
