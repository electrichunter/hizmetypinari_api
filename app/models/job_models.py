import enum
from sqlalchemy import (Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, DECIMAL, CheckConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base # Modüler yapı için 'base.py' dosyasından import ediyoruz

# SQL'deki ENUM tiplerini Python'da tanımlıyoruz
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

# 'categories' tablosu için SQLAlchemy modeli
class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    slug = Column(String(150), nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Kategori ile hizmetler arasındaki ilişki (bir kategori -> çok hizmet)
    services = relationship("Service", back_populates="category")

# 'services' tablosu için SQLAlchemy modeli
class Service(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    name = Column(String(150), nullable=False)
    slug = Column(String(150), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    # Hizmet ile kategori arasındaki ilişki
    category = relationship("Category", back_populates="services")
    # Hizmet ile ilanlar arasındaki ilişki (bir hizmet -> çok ilan)
    jobs = relationship("Job", back_populates="service")

# 'jobs' tablosu için SQLAlchemy modeli
class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True) # SQL'deki BIGINT'i karşılar
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    district_id = Column(Integer, ForeignKey('districts.id'), nullable=False) # district modeli ayrı bir dosyada olacak
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.open)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # İlan ile müşteri (user) arasındaki ilişki
    customer = relationship("User", back_populates="jobs")
    # İlan ile hizmet arasındaki ilişki
    service = relationship("Service", back_populates="jobs")
    # İlan ile teklifler arasındaki ilişki (bir ilan -> çok teklif)
    offers = relationship("Offer", back_populates="job", cascade="all, delete-orphan")
    # İlan ile değerlendirme arasındaki ilişki (bir ilan -> bir değerlendirme)
    review = relationship("Review", back_populates="job", uselist=False, cascade="all, delete-orphan")
    # İlan ile ilçe arasındaki ilişki
    district = relationship("District", back_populates="jobs")


# 'offers' tablosu için SQLAlchemy modeli
class Offer(Base):
    __tablename__ = 'offers'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False) # provider modeli ayrı bir dosyada olacak
    offer_price = Column(DECIMAL(10, 2), nullable=False)
    message = Column(Text)
    status = Column(Enum(OfferStatus), default=OfferStatus.pending)

    # Teklif ile ilan arasındaki ilişki
    job = relationship("Job", back_populates="offers")
    # Teklif ile hizmet sağlayıcı arasındaki ilişki
    provider = relationship("Provider", back_populates="offers")

# 'reviews' tablosu için SQLAlchemy modeli
class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False, unique=True) # Bir işe sadece bir yorum
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Değerlendirme ile ilan arasındaki ilişki
    job = relationship("Job", back_populates="review")
    # Değerlendirme ile müşteri arasındaki ilişki
    customer = relationship("User")
    # Değerlendirme ile hizmet sağlayıcı arasındaki ilişki
    provider = relationship("Provider")

