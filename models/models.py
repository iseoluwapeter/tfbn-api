from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import session
from database import Base
import uuid



class Devotional(Base):
    __tablename__ = "devotionals"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    uuid = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    content = Column(String)
    scripture = Column(String)
    date = Column(String)
    image_url = Column(String)
    prayer= Column(String)
    reading = Column(String)
 
class Events(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    image_url = Column(String)
    title = Column(String)
    date = Column(String)

class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, index=True, nullable=True)
    fullname = Column(String, nullable=True)
    password = Column(String, nullable=True)
    email = Column(String, nullable=True)