import uuid
from typing import List
from pydantic import BaseModel, Field

# Kullanıcı rolleri için olası değerler
ALLOWED_ROLES = ["admin", "customer"]

class UserInDB(BaseModel):
    """Veritabanındaki kullanıcı verilerini temsil eder (Admin Görüntüleme için)."""
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role_name: str = Field(..., description=f"Olası roller: {ALLOWED_ROLES}")

    class Config:
        # FastAPI'nin UUID'yi JSON'a çevirmesi için gerekli
        orm_mode = True 

class UserUpdateRole(BaseModel):
    """Kullanıcının rolünü güncellemek için gelen veriyi temsil eder."""
    new_role: str = Field(..., description="Yeni rol adı (admin veya customer).")
