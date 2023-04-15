import os
import boto3

ALLOW_EXTENSIONS = {
    "image": ["png", "jpg", "jpeg", "bmp", "gif"],
    "video": ["mp4", "mov", "avi", "flv"],
    "music": ["mp3", "wav", "m4a"],
    "zip": ["zip"],
    "model": ["gltf", "fbx"],
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
