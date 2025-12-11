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

    # Coordenadas del pin
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Fecha de creación (para parpadeo en el mapa)
    created_at = Column(DateTime, default=datetime.utcnow)
