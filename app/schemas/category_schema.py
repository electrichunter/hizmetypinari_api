from pydantic import BaseModel
from typing import Optional, List

class ServiceBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    is_active: bool = True

class ServiceCreate(ServiceBase):
    category_id: int

class Service(ServiceBase):
    id: int
    category_id: int

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    services: List[Service] = []

    class Config:
        from_attributes = True
