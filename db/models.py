from typing import Any
from sqlalchemy import Column, String, Enum, ForeignKey, DateTime, Boolean
from uuid import uuid4
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import relationship
import enum
import datetime
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
    profile = Column(String(length=500), nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    works = relationship('Work', foreign_keys='Work.user_id', back_populates='user')
    assets = relationship('Asset', foreign_keys='Asset.user_id')
    tokens = relationship('Token', foreign_keys='Token.user_id')

class Token(Base):
    refresh_token = Column(String(length=255), primary_key=True, default=generate_uuid)
    user_id = Column(String(length=255), ForeignKey('user.id'))
    expired_at = Column(DateTime, default=func.now() + datetime.timedelta(days=14))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user = relationship('User', back_populates='tokens')

class Tagging(Base):

    __tablename__ = 'taggings'

    work_id = Column(String(length=255), ForeignKey('works.id'), primary_key=True)
    tag_id = Column(String(length=255), ForeignKey('tags.id'), primary_key=True)

class Work(Base):

    __tablename__ = 'works'

    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    title = Column(String(length=100))
    description = Column(String)
    description_html = Column(String)
    user_id = Column(String(length=255), ForeignKey('user.id'))
    github_url = Column(String, nullable=True)
    work_url = Column(String, nullable=True)
    community_id = Column(String(length=255), ForeignKey('communities.id'))
    assets = relationship('Asset', foreign_keys='Asset.work_id')
    private = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship('User', back_populates='works')
    community = relationship('Community', back_populates='works')

    tags = relationship(
        'Tag',
        secondary=Tagging.__tablename__,
        back_populates='works'
    )

class Asset(Base):
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    work_id = Column(String(length=255), ForeignKey('works.id'))
    asset_type = Column(Enum(AssetType))
    thumb_url = Column(String, nullable=True)
    url = Column(String, nullable=True)
    user_id = Column(String(length=255), ForeignKey('user.id'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Tag(Base):

    __tablename__='tags'

    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    name = Column(String(length=32))
    community_id = Column(String(length=255), ForeignKey('communities.id'), nullable=True)
    color = Column(String)  
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    works = relationship(
        'Work',
        secondary=Tagging.__tablename__,
        back_populates="tags"
    )

    community = relationship('Community', back_populates='tags')

class Community(Base):

    __tablename__='communities'

    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    name = Column(String(length=32))
    description = Column(String)
    description_html = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    works = relationship('Work', back_populates='community')

    tags = relationship('Tag', back_populates='community')