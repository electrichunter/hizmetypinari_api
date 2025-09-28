from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- Basit Şemalar (İlişkili Verileri Göstermek İçin) ---

class UserSimple(BaseModel):
    """İlan detaylarında gösterilecek basit kullanıcı bilgisi."""
    id: int
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

class ServiceSimple(BaseModel):
    """İlan listesinde gösterilecek basit hizmet bilgisi."""
    id: int
    name: str

    class Config:
        from_attributes = True

class DistrictSimple(BaseModel):
    """İlan listesinde gösterilecek basit ilçe bilgisi."""
    id: int
    name: str

    class Config:
        from_attributes = True


# --- Ana İlan Şemaları ---

class JobBase(BaseModel):
    """İlan oluşturma için temel alanlar."""
    title: str = Field(..., min_length=10, max_length=255, description="İlanın başlığı")
    description: str = Field(..., min_length=20, description="İşin detaylı açıklaması")
    service_id: int = Field(..., description="İlgili hizmetin ID'si")
    district_id: int = Field(..., description="İşin yapılacağı ilçenin ID'si")

class JobCreate(JobBase):
    """Yeni bir ilan oluşturmak için API'ye gönderilecek veri modeli."""
    pass

class JobResponse(JobBase):
    """API'den tek bir ilan detayı dönerken kullanılacak şema."""
    id: int
    status: str
    created_at: datetime
    customer: UserSimple # Müşteri bilgisini de iç içe gösterir

    class Config:
        from_attributes = True # SQLAlchemy modelleriyle uyumlu çalışmasını sağlar

class JobListResponse(BaseModel):
    """API'den ilan listesi dönerken kullanılacak şema."""
    id: int
    title: str
    status: str
    service: ServiceSimple
    district: DistrictSimple
    created_at: datetime

    class Config:
        from_attributes = True
