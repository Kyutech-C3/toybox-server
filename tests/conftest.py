import os
import boto3
import time
from logging import INFO, ERROR, getLogger

S3_BUCKET = os.environ.get('S3_BUCKET')
S3_DIR = os.environ.get('S3_DIR')
REGION_NAME = os.environ.get('REGION_NAME')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_ACCESS_KEY = os.environ.get('SECRET_ACCESS_KEY')

wasabi = boto3.client("s3", endpoint_url = f"https://s3.{REGION_NAME}.wasabisys.com", aws_access_key_id = ACCESS_KEY, aws_secret_access_key = SECRET_ACCESS_KEY)

logger = getLogger('Session Finish')

def pytest_sessionfinish():
    response = wasabi.list_objects_v2(Bucket=S3_BUCKET, Prefix=f"{S3_DIR}/image/")
    for obj in response['Contents']:
        time.sleep(0.5)
        response = wasabi.delete_object(
            Bucket = S3_BUCKET,
            Key = obj['Key'].replace('/origin.png','')
        )

        if response['ResponseMetadata']['HTTPStatusCode'] is 204:
            logger.info(obj['Key'].replace('/origin.png',''))
            logger.info(response)
        else:
            logger.error(obj['Key'].replace('/origin.png',''))
            logger.error(response)
