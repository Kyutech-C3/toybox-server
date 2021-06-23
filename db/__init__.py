import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from .models import *
import os

DATABASE = 'postgresql'
USER = os.environ.get('POSTGRES_USER')
PASSWORD = os.environ.get('POSTGRES_PASSWORD')
HOST = os.environ.get('POSTGRES_HOST')
DB_NAME = os.environ.get('POSTGRES_DB')

DATABASE_URL = "{}://{}:{}@{}/{}".format(DATABASE, USER, PASSWORD, HOST, DB_NAME)

ECHO_LOG = False

engine = sqlalchemy.create_engine(DATABASE_URL, echo=ECHO_LOG)

Base.metadata.create_all(bind=engine)

SessionClass = sessionmaker(engine)


def get_db() -> Session:
    db = SessionClass()
    try:
        yield db
    finally:
        db.close()