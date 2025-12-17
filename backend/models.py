from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from database import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    message = Column(String, nullable=False)
    country = Column(String, nullable=True)
    emoji = Column(String, default="📍")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    hidden = Column(Boolean, default=False)  # 👈 SOFT DELETE
