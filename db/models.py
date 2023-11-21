import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func

from utils.db import generate_uuid

from .blogs.models import BlogTagging
from .db import Base, Column
from .enums import AssetType, UrlType, Visibility

# 2 weeks
DEFAULT_REFRESH_TOKEN_EXPIRED_DAYS = 14


class Favorite(Base):
    __tablename__ = "favorite"

    work_id = Column(
        String(length=255), ForeignKey("works.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = Column(
        String(length=255), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    created_at = Column(DateTime, default=func.now())
    work = relationship("Work", backref="favorite_info")
    user = relationship("User", backref="favorite_info")


class User(Base):
    __tablename__ = "user"
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    name = Column(String(length=32))
    email = Column(String(length=255), unique=True)
    password_hash = Column(String, nullable=True)
    display_name = Column(String(length=32))
    discord_token = Column(String, nullable=True)
    discord_refresh_token = Column(String, nullable=True)
    discord_user_id = Column(String(length=18), nullable=True)
    profile = Column(String(length=500), nullable=True)
    avatar_url = Column(String, nullable=True)
    twitter_id = Column(String, nullable=True)
    github_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    works = relationship("Work", foreign_keys="Work.user_id", back_populates="user")
    assets = relationship("Asset", foreign_keys="Asset.user_id")
    urls = relationship("UrlInfo", foreign_keys="UrlInfo.user_id")
    tokens = relationship("Token", foreign_keys="Token.user_id")
    comments = relationship("Comment", back_populates="user")
    blogs = relationship("Blog", foreign_keys="Blog.user_id", back_populates="user")


class Token(Base):
    refresh_token = Column(String(length=255), primary_key=True, default=generate_uuid)
    user_id = Column(String(length=255), ForeignKey("user.id", ondelete="CASCADE"))
    expired_at = Column(DateTime, default=func.now() + datetime.timedelta(days=14))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="tokens")


class Tagging(Base):
    __tablename__ = "taggings"

    work_id = Column(
        String(length=255), ForeignKey("works.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id = Column(
        String(length=255), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )


class Thumbnail(Base):
    __tablename__ = "thumbnails"
    work_id = Column(
        String(length=255), ForeignKey("works.id", ondelete="CASCADE"), primary_key=True
    )
    asset_id = Column(
        String(length=255), ForeignKey("asset.id", ondelete="CASCADE"), primary_key=True
    )


class Work(Base):
    __tablename__ = "works"

    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    title = Column(String(length=100))
    description = Column(String)
    description_html = Column(String)
    user_id = Column(
        String(length=255), ForeignKey("user.id", ondelete="CASCADE"), nullable=True
    )
    visibility = Column(Enum(Visibility))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="works")
    assets = relationship("Asset", foreign_keys="Asset.work_id", back_populates="work")
    urls = relationship(
        "UrlInfo", foreign_keys="UrlInfo.work_id", back_populates="work"
    )

    tags = relationship("Tag", secondary=Tagging.__tablename__, back_populates="works")

    comments = relationship("Comment", back_populates="work")

    thumbnail = relationship(
        "Asset",
        secondary=Thumbnail.__tablename__,
        back_populates="work_for_thumbnail",
        uselist=False,
    )


class Asset(Base):
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    work_id = Column(
        String(length=255), ForeignKey("works.id", ondelete="CASCADE"), nullable=True
    )
    asset_type = Column(Enum(AssetType))
    user_id = Column(String(length=255), ForeignKey("user.id"))
    extension = Column(String(length=255))
    url = Column(String(length=255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="assets")
    work = relationship("Work", foreign_keys=[work_id], back_populates="assets")

    work_for_thumbnail = relationship(
        "Work", secondary=Thumbnail.__tablename__, back_populates="thumbnail"
    )


class UrlInfo(Base):
    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    work_id = Column(
        String(length=255), ForeignKey("works.id", ondelete="CASCADE"), nullable=True
    )
    url = Column(String(length=255))
    url_type = Column(Enum(UrlType))
    user_id = Column(String(length=255), ForeignKey("user.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="urls")
    work = relationship("Work", foreign_keys=[work_id], back_populates="urls")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    name = Column(String(length=32))
    color = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    works = relationship("Work", secondary=Tagging.__tablename__, back_populates="tags")
    blogs = relationship(
        "Blog", secondary=BlogTagging.__tablename__, back_populates="tags"
    )


class Comment(Base):
    __tablename__ = "comment"

    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    content = Column(String, nullable=False)
    work_id = Column(String, ForeignKey("works.id", ondelete="CASCADE"))
    user_id = Column(String, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    reply_at = Column(String, nullable=True)
    visibility = Column(Enum(Visibility))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="comments")
    work = relationship("Work", back_populates="comments")
