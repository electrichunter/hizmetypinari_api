from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    slug = Column(String(150), nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    services = relationship("Service", back_populates="category")

class Service(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    name = Column(String(150), nullable=False)
    slug = Column(String(150), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    category = relationship("Category", back_populates="services")
    jobs = relationship("Job", back_populates="service")
