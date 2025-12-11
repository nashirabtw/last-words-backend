from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    country = Column(String, nullable=False)
    emoji = Column(String, nullable=False)

    # Ubicación
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Para parpadeo "nuevo" y orden temporal
    created_at = Column(DateTime, default=datetime.utcnow)
