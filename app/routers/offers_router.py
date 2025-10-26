from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from datetime import datetime

# --- Basit Şemalar (İlişkili Verileri Göstermek İçin) ---

class ProviderSimple(BaseModel):
    """Teklif listesinde gösterilecek basit provider bilgisi."""
    id: int # Bu, 'providers' tablosunun ID'sidir
    business_name: Optional[str] = None
    
    # Not: Router'da bu şemayı doldururken, provider.user.first_name gibi
    # ek verileri de birleştirip döndürebiliriz, ancak şema basit kalmalı.

    class Config:
        from_attributes = True

# --- Ana Teklif Şemaları ---

class OfferBase(BaseModel):
    """Teklif oluşturmak için temel alanlar."""
    offer_price: Decimal = Field(..., gt=0, description="Teklif edilen fiyat (0'dan büyük olmalı)")
    message: Optional[str] = Field(None, max_length=1000, description="Hizmet sağlayıcının müşteriye mesajı")

class OfferCreate(OfferBase):
    """
    Yeni bir teklif oluşturmak için API'ye gönderilecek veri modeli.
    'job_id' URL'den alınacak, 'provider_id' ise giriş yapan kullanıcıdan (token) alınacak.
    """
    pass

class OfferResponse(OfferBase):
    """API'den tek bir teklif detayı dönerken kullanılacak şema."""
    id: int
    status: str
    job_id: int
    provider: ProviderSimple # Teklifi yapan provider'ın basit bilgisi

    class Config:
        from_attributes = True # SQLAlchemy modelleriyle uyumlu çalışmasını sağlar

