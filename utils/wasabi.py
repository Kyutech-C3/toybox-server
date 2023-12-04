import os
from typing import Optional

import boto3
import botocore

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
BLOG_S3_DIR = f"{S3_DIR}_blog"
REGION_NAME = os.environ.get("REGION_NAME")
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_ACCESS_KEY = os.environ.get("SECRET_ACCESS_KEY")

wasabi = boto3.client(
    "s3",
    endpoint_url=f"https://s3.{REGION_NAME}.wasabisys.com",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_ACCESS_KEY,
)


def init_wasabi_for_test(
    minio_host: str,
    minio_port: int = 9000,
    access_key: str = ACCESS_KEY,
    secret_access_key: str = SECRET_ACCESS_KEY,
    bucket_name: str = S3_BUCKET,
):
    global wasabi
    wasabi = boto3.client(
        "s3",
        endpoint_url=f"http://{minio_host}:{minio_port}",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
    )
    try:
        wasabi.create_bucket(Bucket=bucket_name)
    except wasabi.exceptions.NoSuchBucket:
        pass


def upload_asset(
    asset_id: str,
    file_bin: bytes,
    extension: str,
    is_blog: bool = False,
) -> Optional[str]:
    extension = extension.lower()
    asset_type = ""
    for type, allow_extension in ALLOW_EXTENSIONS.items():
        if extension in allow_extension:
            asset_type = type
    if asset_type == "":
        return

    s3_dir = BLOG_S3_DIR if is_blog else S3_DIR
    key = f"{s3_dir}/{asset_type}/{asset_id}/origin.{extension}"
    try:
        wasabi.put_object(
            Body=file_bin,
            Bucket=S3_BUCKET,
            Key=key,
            ContentType=MIME_TYPE_DICT.get(extension, MIME_TYPE_DICT["default"]),
        )
    except botocore.exceptions.ClientError as e:
        print(e)
        return

    return f"https://s3.{REGION_NAME}.wasabisys.com/{S3_BUCKET}/{key}"


def remove_asset(asset_id: str, asset_type: str, extension: str):
    try:
        wasabi.delete_object(
            Bucket=S3_BUCKET, Key=f"{S3_DIR}/{asset_type}/{asset_id}/origin.{extension}"
        )
    except botocore.exceptions.ClientError as e:
        print(e)


def upload_avatar(
    user_id: str, file_bin: bytes, extension: str, size: int = 256
) -> Optional[str]:
    extension = extension.lower()
    if extension not in ALLOW_EXTENSIONS["image"]:
        return
    key = f"{S3_DIR}/avatar/{user_id}_{size}.{extension}"
    try:
        wasabi.put_object(
            Body=file_bin,
            Bucket=S3_BUCKET,
            Key=key,
            ContentType=MIME_TYPE_DICT.get(extension, MIME_TYPE_DICT["default"]),
        )
    except botocore.exceptions.ClientError as e:
        print(e)
        return
    return f"https://s3.{REGION_NAME}.wasabisys.com/{S3_BUCKET}/{key}"


def delete_avatar(user_id: str, extension: str, size: int = 256):
    try:
        wasabi.delete_object(
            Bucket=S3_BUCKET, Key=f"{S3_DIR}/avatar/{user_id}_{size}.{extension}"
        )
    except botocore.exceptions.ClientError as e:
        print(e)
