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
    mistaketracker = relationship("MistakeTracker",back_populates="user",uselist = False)


class MistakeLetter(Base, TimeStamps):
    __tablename__ = "MistakeLetter"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"),unique=True)
    jon = Column(MutableDict.as_mutable(JSON))
    user = relationship("User",back_populates = "mistakeletter")

class MistakeTracker(Base,TimeStamps):
    __tablename__ = "MistakeTracker"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"),unique=True)
    count = Column(MutableDict.as_mutable(JSON))
    user = relationship("User",back_populates = "mistaketracker")


class Report(Base,TimeStamps):
    __tablename__ = "reports"

    id = Column(Integer,primary_key = True,index = True)
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable = False)
    session_id = Column(String(64),unique = True,nullable = False,default=lambda x:str(uuid.uuid4()))
    wpm = Column(Float)
    rwpm = Column(Float)
    accuracy = Column(Float)
    second = Column(Integer)
    file_path = Column(String(255),nullable = False)
    user = relationship("User",back_populates = "report")
