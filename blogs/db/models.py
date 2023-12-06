from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func

from db import Base, BlogAssetType, Column, Visibility
from utils.db import generate_uuid


class BlogTagging(Base):
    __tablename__ = "blog_tagging"

    blog_id = Column(
        String(length=255), ForeignKey("blogs.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id = Column(
        String(length=255), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )


class BlogThumbnail(Base):
    __tablename__ = "blog_thumbnails"
    blog_id = Column(
        String(length=255), ForeignKey("blogs.id", ondelete="CASCADE"), primary_key=True
    )
    asset_id = Column(
        String(length=255),
        ForeignKey("blog_assets.id", ondelete="CASCADE"),
        primary_key=True,
    )


class BlogAsset(Base):
    __tablename__ = "blog_assets"

    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    blog_id = Column(
        String(length=255), ForeignKey("blogs.id", ondelete="CASCADE"), nullable=True
    )
    asset_type = Column(Enum(BlogAssetType))
    user_id = Column(String(length=255), ForeignKey("user.id"))
    extension = Column(String(length=255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", backref="blog_assets")
    blog = relationship("Blog", foreign_keys=[blog_id], back_populates="assets")


class BlogFavorite(Base):
    __tablename__ = "blog_favorites"

    blog_id = Column(
        String(length=255), ForeignKey("blogs.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = Column(
        String(length=255), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    created_at = Column(DateTime, default=func.now())
    blog = relationship("Blog", backref="blog_favorite_info")
    user = relationship("User", backref="blog_favorite_info")


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(String(length=255), primary_key=True, default=generate_uuid)
    title = Column(String(length=255))
    body_text = Column(String)
    user_id = Column(
        String(length=255), ForeignKey("user.id", ondelete="CASCADE"), nullable=True
    )
    visibility = Column(Enum(Visibility))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    published_at = Column(DateTime, default=func.now(), nullable=True)

    user = relationship("User", back_populates="blogs")
    tags = relationship("Tag", secondary=BlogTagging.__tablename__, backref="blogs")
    thumbnail = relationship(
        "BlogAsset",
        secondary=BlogThumbnail.__tablename__,
        backref="blog_for_thumbnail",
        uselist=False,
    )
    assets = relationship(
        "BlogAsset", foreign_keys="BlogAsset.blog_id", back_populates="blog"
    )
