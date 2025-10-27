from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    job_id: int
    provider_id: int
    customer_id: int

class Review(ReviewBase):
    id: int
    job_id: int
    provider_id: int
    customer_id: int
    created_at: datetime

    class Config:
        from_attributes = True
