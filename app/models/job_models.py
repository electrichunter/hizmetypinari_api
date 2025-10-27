import enum
from sqlalchemy import (Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, DECIMAL)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base
from .user import User
from .category_models import Service
from .district_models import District
from .provider_models import Provider


class JobStatus(str, enum.Enum):
    open = "open"
    assigned = "assigned"
    completed = "completed"
    cancelled = "cancelled"

class OfferStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    withdrawn = "withdrawn"

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    district_id = Column(Integer, ForeignKey('districts.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.open)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("User", back_populates="jobs")
    service = relationship("Service", back_populates="jobs")
    offers = relationship("Offer", back_populates="job", cascade="all, delete-orphan")
    review = relationship("Review", back_populates="job", uselist=False, cascade="all, delete-orphan")
    district = relationship("District", back_populates="jobs")

class Offer(Base):
    __tablename__ = 'offers'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False)
    offer_price = Column(DECIMAL(10, 2), nullable=False)
    message = Column(Text)
    status = Column(Enum(OfferStatus), default=OfferStatus.pending)

    job = relationship("Job", back_populates="offers")
    provider = relationship("Provider", back_populates="offers")

