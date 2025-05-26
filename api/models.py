from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class TimeStamps:
    create_at = Column(DateTime(timezone=True),
                       default=lambda: datetime.utcnow())
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.utcnow(),
                        onupdate=datetime.utcnow())


class User(Base, TimeStamps):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    password = Column(String(128))

    mistakeletter = relationship("MistakeLetter",back_populates="user",uselist = False)
    report = relationship("Report",back_populates = "user")


class MistakeLetter(Base, TimeStamps):
    __tablename__ = "MistakeLetter"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"),unique=True)
    jon = Column(MutableDict.as_mutable(JSON))
    user = relationship("User",back_populates = "mistakeletter")


class Report(Base,TimeStamps):
    __tablename__ = "reports"

    id = Column(Integer,primary_key = True,index = True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable = False)
    session_id = Column(String(64),unique = True,nullable = False,default=lambda x:str(uuid.uuid4()))
    wpm = Column(Float)
    rwpm = Column(Float)
    accuracy = Column(Float)
    file_path = Column(String(255),nullable = False)
    user = relationship("User",back_populates = "report")
