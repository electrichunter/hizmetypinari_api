from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class District(Base):
    __tablename__ = 'districts'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    city_name = Column(String(100), nullable=False)

    jobs = relationship("Job", back_populates="district")
