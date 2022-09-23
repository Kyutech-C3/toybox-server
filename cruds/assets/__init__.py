from distutils import extension
import os, shutil
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from db import models
from schemas.asset import Asset
from schemas.common import DeleteStatus

ALLOW_EXTENSIONS = {
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
    file_extension = filename[filename.rfind('.')+1:].lower()
    if not file_extension in ALLOW_EXTENSIONS.get(asset_type, []):
        raise HTTPException(status_code=400, detail='this file extension is invalid')

    asset_orm = models.Asset(
        asset_type = asset_type,
        user_id = user_id,
        extension = file_extension
    )
    db.add(asset_orm)
    db.commit()
    db.refresh(asset_orm)

    upload_folder = os.environ.get('UPLOAD_FOLDER')
    upload_folder = f'{upload_folder}/{asset_type}/{asset_orm.id}'
    os.makedirs(upload_folder)
    with open(os.path.join(upload_folder, f'origin.{file_extension}'),'wb+') as upload_path:
        shutil.copyfileobj(file.file, upload_path)

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
