from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from ..models.job_models import OfferStatus

class OfferBase(BaseModel):
    offer_price: Decimal
    message: Optional[str] = None

class OfferCreate(OfferBase):
    job_id: int
    provider_id: int

class OfferUpdate(BaseModel):
    status: OfferStatus

class Offer(OfferBase):
    id: int
    job_id: int
    provider_id: int
    status: OfferStatus

    class Config:
        from_attributes = True
