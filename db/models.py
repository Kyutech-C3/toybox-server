from typing import Any
from sqlalchemy import Column, String, Enum, ForeignKey, DateTime
from uuid import uuid4
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import relationship
import enum
import datetime
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.functions import func

# 2 weeks
DEFAULT_REFRESH_TOKEN_EXPIRED_DAYS = 14

def generate_uuid():
    return str(uuid4())

@as_declarative()
class Base:
    id: Any
    __name__: Any

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()

class AssetType(str, enum.Enum):
    image = 'image'
    video = 'video'
    music = 'music'

class User(Base):
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    name = Column(String(length=32))
    email = Column(String(length=255),unique=True)
    password_hash = Column(String, nullable=True)
    display_name = Column(String(length=32))
    discord_token = Column(String, nullable=True)
    discord_refresh_token = Column(String, nullable=True)
    discord_user_id = Column(String(length=18), nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    works = relationship('Work', foreign_keys='Work.user_id')
    assets = relationship('Asset', foreign_keys='Asset.user_id')
    tokens = relationship('Token', foreign_keys='Token.user_id')

class Token(Base):
    refresh_token = Column(String(length=255), primary_key=True, default=generate_uuid)
    user_id = Column(String(length=255), ForeignKey('user.id'))
    expired_at = Column(DateTime, default=func.now() + datetime.timedelta(days=14))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user = relationship('User', back_populates='tokens')

class Work(Base):
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    title = Column(String(length=100))
    description = Column(String)
    description_html = Column(String)
    user_id = Column(String(length=255), ForeignKey('user.id'))
    github_url = Column(String, nullable=True)
    work_url = Column(String, nullable=True)
    community_id = Column(String(length=255), ForeignKey('community.id'))
    assets = relationship('Asset', foreign_keys='Asset.work_id')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Asset(Base):
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    work_id = Column(String(length=255), ForeignKey('work.id'))
    asset_type = Column(Enum(AssetType))
    thumb_url = Column(String, nullable=True)
    url = Column(String, nullable=True)
    user_id = Column(String(length=255), ForeignKey('user.id'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Tag(Base):
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    name = Column(String(length=32))
    community_id = Column(String(length=255), ForeignKey('community.id'), nullable=True)
    color = Column(String)  
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Tagging(Base):
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    work_id = Column(String(length=255), ForeignKey('work.id'))
    tag_id = Column(String(length=255), ForeignKey('tag.id'))

class Community(Base):
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    name = Column(String(length=32))
    description = Column(String)
    description_html = Column(String)
    works = relationship('Work', foreign_keys='Work.community_id')
    tags = relationship('Tag', foreign_keys='Tag.community_id')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
