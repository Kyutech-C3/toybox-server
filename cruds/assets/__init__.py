import os, shutil
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from db import models
from schemas.asset import Asset
from schemas.common import DeleteStatus
import boto3

ALLOW_EXTENTIONS = {
    'image': ['png', 'jpg', 'jpeg', 'bmp', 'gif'],
    'video': ['mp4', 'mov', 'avi', 'flv'],
    'music': ['mp3', 'wav', 'm4a'],
    'zip': ['zip'],
    'model': ['gltf', 'fbx']
}

def create_asset(db: Session, user_id: str, asset_type: str, file: UploadFile) -> Asset:
    filename = file.filename
    if filename == '':
        raise HTTPException(status_code=400, detail='this file is invalid')
    file_extention = filename[filename.rfind('.')+1:].lower()
    if not file_extention in ALLOW_EXTENTIONS.get(asset_type, []):
        raise HTTPException(status_code=400, detail='this file extention is invalid')

    asset_orm = models.Asset(
        asset_type = asset_type,
        user_id = user_id,
        extention = file_extention,
        url = ''
    )
    db.add(asset_orm)
    db.commit()
    db.refresh(asset_orm)

    s3_bucket = os.environ.get('S3_BUCKET')
    s3_dir = os.environ.get('S3_DIR')
    region_name = os.environ.get('REGION_NAME')
    ACCESS_KEY = os.environ.get('ACCESS_KEY')
    SECRET_ACCESS_KEY = os.environ.get('SECRET_ACCESS_KEY')

    wasabi = boto3.client("s3", endpoint_url = f"https://s3.{region_name}.wasabisys.com", aws_access_key_id = ACCESS_KEY, aws_secret_access_key = SECRET_ACCESS_KEY)
    response = wasabi.put_object(
        Body = file.file,
        Bucket = s3_bucket,
        Key = f"{s3_dir}/{asset_type}/{asset_orm.id}/origin.{file_extention}"
    )

    file_url = "https://s3.%s.wasabisys.com/%s" % (region_name, f"{s3_bucket}/{s3_dir}/{asset_type}/{asset_orm.id}/origin.{file_extention}")
    print(file_url)

    print(response)

    asset_orm.url = file_url
    db.commit()
    db.refresh(asset_orm)

    asset = Asset.from_orm(asset_orm)
    return asset

def delete_asset_by_id(db: Session, asset_id: str) -> DeleteStatus:
    asset_orm = db.query(models.Asset).get(asset_id)
    if asset_orm is None:
        raise HTTPException(status_code=404, detail='this asset is not exist')

    upload_folder = os.environ.get('UPLOAD_FOLDER')
    upload_folder = f'{upload_folder}/{asset_orm.asset_type}/{asset_orm.id}'
    shutil.rmtree(upload_folder)

    db.delete(asset_orm)
    db.commit()

    return {'status': 'OK'}
