import os
import boto3
import botocore
from typing import Optional

ALLOW_EXTENSIONS = {
    "image": ["png", "jpg", "jpeg", "bmp", "gif", "webp"],
    "video": ["mp4", "mov", "avi", "flv"],
    "music": ["mp3", "wav", "m4a"],
    "zip": ["zip"],
    "model": ["gltf", "fbx"],
}

MIME_TYPE_DICT = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "bmp": "image/bmp",
    "gif": "image/gif",
    "webp": "image/webp",
    "mp4": "video/mp4",
    "mov": "video/quicktime",
    "avi": "video/x-msvideo",
    "flv": "video/x-flv",
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "m4a": "audio/aac",
    "zip": "application/zip",
    "gltf": "model/gltf+json",
    "default": "application/octet-stream",
}

S3_BUCKET = os.environ.get("S3_BUCKET")
S3_DIR = os.environ.get("S3_DIR")
REGION_NAME = os.environ.get("REGION_NAME")
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_ACCESS_KEY = os.environ.get("SECRET_ACCESS_KEY")

wasabi = boto3.client(
    "s3",
    endpoint_url=f"https://s3.{REGION_NAME}.wasabisys.com",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_ACCESS_KEY,
)


def upload_avatar(user_id: str, file_bin: bytes, extension: str) -> Optional[str]:
    extension = extension.lower()
    if extension not in ALLOW_EXTENSIONS["image"]:
        return
    try:
        wasabi.put_object(
            Body=file_bin,
            Bucket=S3_BUCKET,
            Key=f"{S3_DIR}/avatar/{user_id}.{extension}",
            ContentType=MIME_TYPE_DICT.get(extension, MIME_TYPE_DICT["default"]),
        )
    except botocore.exceptions.ClientError as e:
        print(e)
        return
    return f"https://s3.ap-northeast-2.wasabisys.com/{S3_BUCKET}/{S3_DIR}/avatar/{user_id}.{extension}"


def delete_avatar(user_id: str, extension: str):
    try:
        wasabi.delete_object(
            Bucket=S3_BUCKET, Key=f"{S3_DIR}/avatar/{user_id}.{extension}"
        )
    except botocore.exceptions.ClientError as e:
        print(e)
        return e
