import json
import os
from datetime import timedelta
from typing import Callable, List, Optional

import pytest
import sqlalchemy
import sqlalchemy_utils
from fastapi.datastructures import UploadFile
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from blogs.db import models as blog_models
from cruds.assets import create_asset
from cruds.tags import create_tag
from cruds.users import auth
from cruds.works import set_work
from db import Base, Visibility, get_db, models
from main import app
from schemas.asset import Asset as AssetSchema
from schemas.tag import GetTag as TagSchema
from schemas.url_info import BaseUrlInfo
from schemas.user import TokenResponse as TokenResponseSchema
from schemas.user import User as UserSchema
from schemas.work import Work as WorkSchema
from utils.wasabi import init_wasabi_for_test

DATABASE = "postgresql"
USER = os.environ.get("POSTGRES_USER")
PASSWORD = os.environ.get("POSTGRES_PASSWORD")
HOST = os.environ.get("POSTGRES_HOST")
DB_NAME = "toybox_test"

DATABASE_URL = "{}://{}:{}@{}/{}".format(DATABASE, USER, PASSWORD, HOST, DB_NAME)

ECHO_LOG = False

client = TestClient(app)

engine = sqlalchemy.create_engine(DATABASE_URL, echo=ECHO_LOG)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

MINIO_HOST = os.environ.get("MINIO_HOST")
MINIO_PORT = os.environ.get("MINIO_PORT")
init_wasabi_for_test(minio_host=MINIO_HOST, minio_port=MINIO_PORT)


@pytest.fixture(scope="function")
def use_test_db_fixture():
    """
    Override get_db with test DB
    get_db関数をテストDBで上書きする
    """
    if not sqlalchemy_utils.database_exists(DATABASE_URL):
        print("[INFO] CREATE DATABASE")
        sqlalchemy_utils.create_database(DATABASE_URL)

    # Reset test tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    def override_get_db():
        try:
            db = SessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield SessionLocal()


@pytest.fixture
def session_for_test():
    """
    DB Session for test
    """
    session = SessionLocal()
    yield session

    session.close()


@pytest.fixture
def user_factory_for_test(
    session_for_test: Session,
) -> Callable[[Session, str, str, str], UserSchema]:
    """
    Create test user
    """

    def user_for_test(
        session_for_test: Session = session_for_test,
        email: str = "test@test.com",
        name: str = "iamtestuser",
        display_name: str = "I am Test User",
    ) -> UserSchema:
        u = models.User(email=email, name=name, display_name=display_name)
        session_for_test.add(u)
        session_for_test.commit()
        return UserSchema.from_orm(u)

    return user_for_test


@pytest.fixture
def users_factory_for_test(
    session_for_test: Session,
) -> Callable[[Session, str, str, str], UserSchema]:
    """
    Create test user
    """

    def users_for_test(session_for_test: Session = session_for_test) -> UserSchema:
        user_list = []
        with open("./tests/test_data/test_user.json") as f:
            test_users = json.load(f)
            for test_user in test_users:
                user = models.User(
                    email=test_users[test_user]["email"],
                    name=test_users[test_user]["name"],
                    display_name=test_users[test_user]["display_name"],
                )
                session_for_test.add(user)
                session_for_test.commit()
                session_for_test.refresh(user)
                user = UserSchema.from_orm(user)
                user_list.append(user)
        return user_list

    return users_for_test


@pytest.fixture
def user_for_test(
    session_for_test: Session,
    email: str = "test@test.com",
    name: str = "iamtestuser",
    display_name: str = "I am Test User",
) -> UserSchema:
    u = models.User(email=email, name=name, display_name=display_name)
    session_for_test.add(u)
    session_for_test.commit()
    return UserSchema.from_orm(u)


@pytest.fixture
def user_token_factory_for_test(
    session_for_test: Session,
    user_for_test: UserSchema,
) -> Callable[[timedelta, timedelta], TokenResponseSchema]:
    """
    Create test user's token
    """
    user = (
        session_for_test.query(models.User)
        .filter(models.User.id == user_for_test.id)
        .first()
    )

    def factory(
        access_token_expires_delta: timedelta = timedelta(minutes=15),
        refresh_token_expires_delta: timedelta = timedelta(days=14),
    ):
        t = auth.create_refresh_token(
            user, session_for_test, refresh_token_expires_delta
        )
        access_token = auth.create_access_token(user, access_token_expires_delta)
        token = TokenResponseSchema(
            refresh_token=t.refresh_token,
            expired_at=t.expired_at.isoformat(),
            access_token=access_token,
        )
        return token

    return factory


@pytest.fixture
def work_factory_for_test(
    session_for_test: Session,
    user_for_test: UserSchema,
    asset_factory_for_test: Callable[[Session, str, UploadFile], AssetSchema],
) -> Callable[[Session, str, str], WorkSchema]:
    def work_for_test(
        session_for_test: Session = session_for_test,
        title: str = "WorkTitleForTest",
        description: str = "this work is test",
        visibility: str = Visibility.public,
        asset_types: List[str] = ["image"],
        urls: List[BaseUrlInfo] = [],
        tags_id: List[str] = [],
        user_id: Optional[str] = None,
    ) -> WorkSchema:
        """
        Create test work
        """
        thumbnail_id = asset_factory_for_test().id
        assets_id = []

        for asset_type in asset_types:
            if asset_type == "zip":
                asset = asset_factory_for_test(
                    session_for_test, "zip", UploadFile("tests/test_data/test_zip.zip")
                )
            if asset_type == "image":
                asset = asset_factory_for_test(
                    session_for_test,
                    "image",
                    UploadFile("tests/test_data/test_image.png"),
                )
            if asset_type == "video":
                asset = asset_factory_for_test(
                    session_for_test,
                    "video",
                    UploadFile("tests/test_data/test_video.mp4"),
                )
            if asset_type == "music":
                asset = asset_factory_for_test(
                    session_for_test,
                    "music",
                    UploadFile("tests/test_data/test_music.wav"),
                )
            if asset_type == "model":
                asset = asset_factory_for_test(
                    session_for_test,
                    "model",
                    UploadFile("tests/test_data/test_model.gltf"),
                )
            assets_id.append(asset.id)

        user_id_for_work = user_id if user_id else user_for_test.id

        w = set_work(
            session_for_test,
            title,
            description,
            user_id_for_work,
            visibility,
            thumbnail_id,
            assets_id,
            urls,
            tags_id,
        )
        return w

    return work_for_test


@pytest.fixture
def asset_factory_for_test(
    session_for_test: Session,
    user_for_test: UserSchema,
) -> Callable[[Session, str, UploadFile], AssetSchema]:
    def asset_for_test(
        session_for_test: Session = session_for_test,
        asset_type: str = "image",
        file: UploadFile = UploadFile("tests/test_data/test_image.png"),
    ) -> AssetSchema:
        """
        Create test asset
        """
        a = create_asset(
            session_for_test,
            user_for_test.id,
            asset_type,
            file,
            extension="png",
        )
        return a

    return asset_for_test


@pytest.fixture
def image_asset_for_test(
    session_for_test: Session,
    user_factory_for_test: Callable[[Session, str, str, str], UserSchema],
    asset_type: str = "image",
    file: UploadFile = UploadFile("tests/test_data/test_image.png"),
) -> AssetSchema:
    u = user_factory_for_test()
    a = create_asset(session_for_test, u.id, asset_type, file, extension="png")
    return a


@pytest.fixture
def tag_for_test(
    session_for_test: Session, name: str = "test_tag", color: str = "#ffffff"
) -> TagSchema:
    """
    Create test tag
    """
    c = create_tag(session_for_test, name, color)
    return c


@pytest.fixture
def tags_for_test(session_for_test: Session) -> list[TagSchema]:
    """
    Create test tags
    """
    tags = [
        {"id": "tag1", "name": "test1_tag1", "color": "#fffffa"},
        {"id": "tag2", "name": "test1_tag2", "color": "#fffffb"},
        {"id": "tag3", "name": "test1_tag3", "color": "#fffffc"},
        {"id": "tag4", "name": "test1_tag4", "color": "#fffffd"},
        {"id": "tag8", "name": "test1_tag8", "color": "#fffffb"},
        {"id": "tag9", "name": "test1_tag9", "color": "#fffffc"},
        {"id": "tag5", "name": "test2_tag5", "color": "#fffffe"},
        {"id": "tag6", "name": "test2_tag6", "color": "#ffffff"},
        {"id": "tag7", "name": "test2_tag7", "color": "#fffffa"},
    ]

    c: list = []

    for tag in tags:
        c.append(create_tag(session_for_test, tag["name"], tag["color"]))

    return c


@pytest.fixture
def tag_factory_for_test(
    session_for_test: Session,
) -> Callable[[str, str], TagSchema]:
    def tag_for_test(name: str = "test_tag", color: str = "#FFFFFF") -> TagSchema:
        """
        Create test tag
        """
        c = create_tag(session_for_test, name, color)
        return c

    return tag_for_test
