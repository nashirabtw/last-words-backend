from sqlalchemy import Column, Integer, String
from .database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    country = Column(String, nullable=True)
    emoji = Column(String, nullable=True)
