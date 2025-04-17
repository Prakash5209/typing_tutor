from sqlalchemy import Column,Integer,String
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class MistypeModel(Base):
    __tablename__ = "mistypecontainer"
    id = Column(Integer,primary_key=True,index=True)
    expected = Column(String(1))
    typed = Column(String(1))
    timestamp = Column(DateTime)

    def __repr__(self):
        return f"id:{self.id}"
