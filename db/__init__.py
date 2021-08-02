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

# Create database for test
def create_test_database():
    DATABASE_URL = "{}://{}:{}@{}".format(DATABASE, USER, PASSWORD, HOST)
    engine = sqlalchemy.create_engine(DATABASE_URL, echo=ECHO_LOG)
    session = Session(
        bind=engine,
        autocommit=True,
        autoflush=True
    )
    session.connection().connection.set_isolation_level(0)
    result = session.execute("SELECT datname from pg_database where datname='%s'" % 'toybox_test')
    if len(result.all()) == 0:
        session.execute("CREATE DATABASE %s WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '%s');" % ('toybox_test', 'toybox_test'))
    session.connection().connection.set_isolation_level(1)
    session.close()

create_test_database()

engine = sqlalchemy.create_engine(DATABASE_URL, echo=ECHO_LOG)

Base.metadata.create_all(bind=engine)

SessionClass = sessionmaker(engine)


def get_db() -> Session:
    db = SessionClass()
    try:
        yield db
    finally:
        db.close()