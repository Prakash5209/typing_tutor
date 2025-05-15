from sqlalchemy import Column, Integer, String, DateTime
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
