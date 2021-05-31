from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Enum, ForeignKey, TIMESTAMP
from uuid import uuid4
from sqlalchemy.orm import relationship
import enum

def generate_uuid():
    return str(uuid4())

Base = declarative_base()

class AssetType(str, enum.Enum):
    image = 'image'
    video = 'video'
    music = 'music'

class User(Base):
    __tablename__ = 'user'
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    name = Column(String(length=32))
    email = Column(String(length=255))
    password_hash = Column(String, nullable=True)
    display_name = Column(String(length=32))
    discord_token = Column(String)
    discord_refresh_token = Column(String)
    discord_user_id = Column(String(length=18))
    avatar_url = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

class Work(Base):
    __tablename__ = 'work'
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    title = Column(String(length=100))
    description = Column(String)
    description_html = Column(String)
    user_id = Column(String(length=255), ForeignKey('user.id'))
    github_url = Column(String, nullable=True)
    work_url = Column(String, nullable=True)
    community_id = Column(String(length=255), ForeignKey('community.id'))

class Asset(Base):
    __tablename__ = 'asset'
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    work_id = Column(String(length=255), ForeignKey('work.id'))
    asset_type = Column(Enum(AssetType))
    thumb_url = Column(String, nullable=True)
    url = Column(String, nullable=True)
    user_id = Column(String(length=255), ForeignKey('user.id'))


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    name = Column(String(length=32))
    community_id = Column(String(length=255), ForeignKey('community.id'), nullable=True)
    color = Column(String)  

class Tagging(Base):
    __tablename__ = 'tagging'
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    work_id = Column(String(length=255), ForeignKey('work.id'))
    tag_id = Column(String(length=255), ForeignKey('tag.id'))

class Community(Base):
    __tablename__ = 'community'
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    name = Column(String(length=32))
    description = Column(String)
    description_html = Column(String)
