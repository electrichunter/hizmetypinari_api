from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Provider(Base):
    __tablename__ = 'providers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    business_name = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    bio = Column(Text)
    
    user = relationship("User", back_populates="provider_profile")
    offers = relationship("Offer", back_populates="provider")
    reviews = relationship("Review", back_populates="provider")
