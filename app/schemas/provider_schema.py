from pydantic import BaseModel
from typing import Optional

class ProviderBase(BaseModel):
    business_name: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool = False

class ProviderCreate(ProviderBase):
    user_id: int

class Provider(ProviderBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
