from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
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


def track_letters():
    return {'a': [0, 0], 'b': [0, 0], 'c': [0, 0], 'd': [0, 0], 'e': [0, 0], 'f': [0, 0], 'g': [0, 0], 'h': [0, 0], 'i': [0, 0], 'j': [0, 0], 'k': [0, 0], 'l': [0, 0], 'm': [0, 0], 'n': [0, 0], 'o': [0, 0], 'p': [0, 0], 'q': [0, 0], 'r': [0, 0], 's': [0, 0], 't': [0, 0], 'u': [0, 0], 'v': [0, 0], 'w': [0, 0], 'x': [0, 0], 'y': [0, 0], 'z': [0, 0]}

class MistakeLetter(Base, TimeStamps):
    __tablename__ = "MistakeLetter"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"),unique=True)
    json = Column(JSON,default = track_letters)
    user = relationship("User",back_populates = "mistakeletter")

