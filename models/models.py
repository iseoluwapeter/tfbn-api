from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import uuid
from datetime import datetime
from slugify import slugify


class Devotional(Base):
    __tablename__ = "devotionals"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    uuid = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    content = Column(Text)
    scripture = Column(String)
    date = Column(String)
    image_url = Column(String)
    prayer = Column(String)
    reading = Column(String)


class Events(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    image_url = Column(String)
    title = Column(String)
    date = Column(String)


class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String)
    password = Column(String)
    email = Column(String)


class Testimonies(Base):
    __tablename__ = "testimonies"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    testimony = Column(String, nullable=False)  
    name = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    articles = relationship("Article", back_populates="category", cascade="all, delete")


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)
    content = Column(Text, nullable=False)
    cover_image = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    author = Column(String, nullable=False)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="articles")
    comments = relationship("Comments", back_populates="article", cascade="all, delete")


class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String)
    email = Column(String)
    comment = Column(Text)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"))
    is_approved = Column(Boolean, default=False)  # ✅ Admin must approve before visible
    is_read = Column(Boolean, default=False)  # ✅ For notification tracking
    created_at = Column(DateTime, default=datetime.utcnow)

    article = relationship("Article", back_populates="comments")
