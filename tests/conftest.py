import shutil
import os

def pytest_sessionfinish():
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    shutil.rmtree(UPLOAD_FOLDER)