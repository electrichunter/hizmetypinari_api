from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Temel Kullanıcı Bilgisi (Değerlendirmeyi yapanı göstermek için)
class ReviewerInfo(BaseModel):
    id: int
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

# Yeni bir değerlendirme oluşturmak için kullanılacak şema
class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Puan (1-5 arası)")
    comment: Optional[str] = Field(None, max_length=1000, description="Yorum metni")

# API'den dönen temel değerlendirme yanıtı
class ReviewResponse(BaseModel):
    id: int
    job_id: int
    provider_id: int
    customer_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Bir sağlayıcının tüm değerlendirmelerini listelerken kullanılacak şema
# Değerlendirmeyi yapan müşterinin bilgilerini de içerir.
class ReviewForProviderResponse(BaseModel):
    id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    customer: ReviewerInfo # Değerlendirmeyi yapan müşteri bilgisi

    class Config:
        from_attributes = True
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Temel Kullanıcı Bilgisi (Değerlendirmeyi yapanı göstermek için)
class ReviewerInfo(BaseModel):
    id: int
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

# Yeni bir değerlendirme oluşturmak için kullanılacak şema
class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Puan (1-5 arası)")
    comment: Optional[str] = Field(None, max_length=1000, description="Yorum metni")

# API'den dönen temel değerlendirme yanıtı
class ReviewResponse(BaseModel):
    id: int
    job_id: int
    provider_id: int
    customer_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Bir sağlayıcının tüm değerlendirmelerini listelerken kullanılacak şema
# Değerlendirmeyi yapan müşterinin bilgilerini de içerir.
class ReviewForProviderResponse(BaseModel):
    id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    customer: ReviewerInfo # Değerlendirmeyi yapan müşteri bilgisi

    class Config:
        from_attributes = True