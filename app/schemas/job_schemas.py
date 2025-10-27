from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .user_schema import UserSimple
from .category_schema import Service
from .district_schema import District
from .offer_schema import Offer
from ..models.job_models import JobStatus

class JobBase(BaseModel):
    title: str = Field(..., min_length=10, max_length=255, description="İlanın başlığı")
    description: str = Field(..., min_length=20, description="İşin detaylı açıklaması")
    service_id: int = Field(..., description="İlgili hizmetin ID'si")
    district_id: int = Field(..., description="İşin yapılacağı ilçenin ID'si")

class JobCreate(JobBase):
    customer_id: Optional[int] = Field(None, description="Admin/Provider tarafından ilan oluşturuluyorsa, müşterinin ID'si")

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    service_id: Optional[int] = None
    district_id: Optional[int] = None
    status: Optional[JobStatus] = None
    is_active: Optional[bool] = None

class Job(JobBase):
    id: int
    customer_id: int
    status: JobStatus
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    customer: UserSimple
    service: Service
    district: District
    offers: List[Offer] = []

    class Config:
        from_attributes = True

