import os
from typing import Any

import sqlalchemy
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

APP_TYPE = os.environ.get("APP_TYPE")

DATABASE = "postgresql"
USER = os.environ.get("POSTGRES_USER")
PASSWORD = os.environ.get("POSTGRES_PASSWORD")
HOST = os.environ.get("POSTGRES_HOST")
DB_NAME = os.environ.get("POSTGRES_DB")

DATABASE_URL = "{}://{}:{}@{}/{}".format(DATABASE, USER, PASSWORD, HOST, DB_NAME)

ECHO_LOG = False


# Create database for test
def create_test_database():
    DATABASE_URL = "{}://{}:{}@{}".format(DATABASE, USER, PASSWORD, HOST)
    engine = sqlalchemy.create_engine(DATABASE_URL, echo=ECHO_LOG)
    session = Session(bind=engine, autocommit=True, autoflush=True)
    session.connection().connection.set_isolation_level(0)
    result = session.execute(
        "SELECT datname from pg_database where datname='%s'" % "toybox_test"
    )
    if len(result.all()) == 0:
        session.execute("CREATE DATABASE %s;" % ("toybox_test"))
    session.connection().connection.set_isolation_level(1)
    session.close()


if APP_TYPE == "dev":
    create_test_database()


@as_declarative()
class Base:
    id: Any
    __name__: Any

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()


class Column(sqlalchemy.Column):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("nullable", False)
        super().__init__(*args, **kwargs)

    inherit_cache: bool = True


engine = sqlalchemy.create_engine(DATABASE_URL, echo=ECHO_LOG)


SessionClass = sessionmaker(engine)


def get_db() -> Session:
    db = SessionClass()
    try:
        yield db
    finally:
        db.close()
