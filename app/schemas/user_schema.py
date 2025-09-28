from pydantic import BaseModel, EmailStr
from ..models.user import RoleName

# Kullanıcı oluşturmak için kullanılacak Pydantic modeli.
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role_name: RoleName

# Kullanıcı verilerini yanıt olarak döndürmek için kullanılacak Pydantic modeli.
# 'orm_mode' yerine 'from_attributes' kullanıldı.
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role_name: RoleName

    class Config:
        from_attributes = True

# JWT token için Pydantic modeli.
class Token(BaseModel):
    access_token: str
    token_type: str

# Kullanıcı girişi için Pydantic modeli.
class UserLogin(BaseModel):
    email: EmailStr
    password: str
