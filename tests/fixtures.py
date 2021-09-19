import sqlalchemy
import pytest
from sqlalchemy.orm import sessionmaker
import sqlalchemy_utils
from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy.orm.session import Session
from sqlalchemy_utils.view import refresh_materialized_view

from db.models import User, Community
from schemas.user import User as UserSchema, Token as TokenSchema, TokenResponse as TokenResponseSchema
from schemas.work import Work as WorkSchema
from schemas.community import Community as CommunitySchema
from db import Base, get_db
from main import app
import os
from datetime import timedelta
from cruds.users import auth
from cruds.works import create_work
from cruds.communities import create_community

DATABASE = 'postgresql'
USER = os.environ.get('POSTGRES_USER')
PASSWORD = os.environ.get('POSTGRES_PASSWORD')
HOST = os.environ.get('POSTGRES_HOST')
DB_NAME = 'toybox_test'

DATABASE_URL = "{}://{}:{}@{}/{}".format(DATABASE, USER, PASSWORD, HOST, DB_NAME)

ECHO_LOG = False

client = TestClient(app)

engine = sqlalchemy.create_engine(DATABASE_URL, echo=ECHO_LOG)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def use_test_db_fixture():
  """
  Override get_db with test DB
  get_db関数をテストDBで上書きする
  """
  if not sqlalchemy_utils.database_exists(DATABASE_URL):
    print('[INFO] CREATE DATABASE')
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
  session_for_test: Session
) -> UserSchema:
  """
  Create test user
  """
  def user_for_test(
    session_for_test: Session = session_for_test,
    email: str = 'test@test.com',
    name: str = 'iamtestuser',
    display_name: str ='I am Test User'
  ) -> UserSchema:
    u = User(email=email, name=name, display_name=display_name)
    session_for_test.add(u)
    session_for_test.commit()
    return UserSchema.from_orm(u)
  return user_for_test

@pytest.fixture
def user_token_factory_for_test(
  session_for_test: Session,
  user_factory_for_test: UserSchema,
) -> TokenResponseSchema:
  """
  Create test user's token
  """
  test_user = user_factory_for_test()
  user = session_for_test.query(User).filter(User.id == test_user.id).first()
  def factory(
    access_token_expires_delta: timedelta = timedelta(minutes=15),
    refresh_token_expires_delta: timedelta = timedelta(days=14)
  ):
    t = auth.create_refresh_token(
      user,
      session_for_test,
      refresh_token_expires_delta
    )
    access_token = auth.create_access_token(user, access_token_expires_delta)
    token = TokenResponseSchema(
      refresh_token=t.refresh_token,
      expired_at=t.expired_at.isoformat(),
      access_token=access_token
    )
    return token
  return factory
    
@pytest.fixture
def community_for_test(
  session_for_test: Session,
  name: str = "test_community",
  description: str = "this is test community"
) -> CommunitySchema:
  """
  Create test community
  """
  c = create_community(session_for_test, name, description)
  return c

@pytest.fixture
def work_for_test_public(
  session_for_test: Session,
  community_for_test: CommunitySchema,
  user_factory_for_test: UserSchema,
  title: str = "testworkpublic",
  description: str = "this is public test work"
) -> WorkSchema:
  """
  Create test public work
  """
  creating_user_for_test = user_factory_for_test(email='publicwork@test.co.jp', name='icreatepublicwork', display_name='I create public work')
  w = create_work(session_for_test, title, description, None, None, creating_user_for_test.id, community_for_test.id, False)
  return w

@pytest.fixture
def work_for_test_private(
  session_for_test: Session,
  community_for_test: CommunitySchema,
  user_factory_for_test: UserSchema,
  title: str = "testworkprivate",
  description: str = "this is private test work"
) -> WorkSchema:
  """
  Create test public work
  """
  creating_user_for_test = user_factory_for_test(email='privatework@test.co.jp', name='icreateprivatework', display_name='I create private work')
  w = create_work(session_for_test, title, description, None, None, creating_user_for_test.id, community_for_test.id, True)
  return w
