# Gerekli kütüphaneler import ediliyor
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, EmailStr 

# ----------------------------------------------------------------------
# SCHEMAS (Veri Modelleri)
# ----------------------------------------------------------------------

class UserInDB(BaseModel):
    """Veritabanındaki kullanıcı verilerini temsil eden model."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Kullanıcının benzersiz ID'si")
    email: EmailStr = Field(..., description="Kullanıcının e-posta adresi", examples=["john.doe@example.com"])
    first_name: str = Field(..., description="Kullanıcının adı")
    last_name: str = Field(..., description="Kullanıcının soyadı")
    role_name: str = Field("customer", description="Kullanıcının rolü ('admin' veya 'customer')")
    password_hash: str = Field(..., description="Parolanın hash'lenmiş hali")
    is_active: bool = Field(True, description="Kullanıcı hesabının aktif olup olmadığı")

class UserPublic(BaseModel):
    """API yanıtları için parola gibi hassas verileri içermeyen model."""
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    role_name: str
    is_active: bool

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": str(uuid.uuid4()),
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "Kullanıcı",
                "role_name": "customer",
                "is_active": True
            }
        }
    }

class UserCreateRequest(BaseModel):
    """Yeni kullanıcı oluşturma isteği için model."""
    email: EmailStr
    first_name: str
    last_name: str
    password: str = Field(..., min_length=6)

class UserUpdateRequest(BaseModel):
    """Kullanıcı bilgilerini güncelleme isteği için model."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserUpdateRoleRequest(BaseModel):
    """Kullanıcı rolü güncelleme isteği için kullanılan model."""
    new_role: str = Field(..., description="Kullanıcının atanacağı yeni rol ('admin' veya 'customer')")

ALLOWED_ROLES = ["admin", "customer"]
# ----------------------------------------------------------------------
# MOCK VERİ (Veritabanı Simülasyonu)
# ----------------------------------------------------------------------
MOCK_USERS: Dict[uuid.UUID, UserInDB] = {}

def initialize_mock_users():
    """Uygulama her yüklendiğinde mock kullanıcı verilerini oluşturur ve günceller."""
    global MOCK_USERS
    MOCK_USERS.clear()

    admin_id = uuid.uuid4()
    MOCK_USERS[admin_id] = UserInDB(
        id=admin_id,
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        role_name="admin",
        password_hash="fake-hashed-password-1"
    )

    customer1_id = uuid.uuid4()
    MOCK_USERS[customer1_id] = UserInDB(
        id=customer1_id, email="customer1@example.com", first_name="Ayşe", last_name="Yılmaz", role_name="customer", password_hash="fake-hashed-password-2"
    )

    customer2_id = uuid.uuid4()
    MOCK_USERS[customer2_id] = UserInDB(
        id=customer2_id, email="customer2@example.com", first_name="Mehmet", last_name="Demir", role_name="customer", password_hash="fake-hashed-password-3"
    )
    # Pasif bir kullanıcı ekleyelim
    customer3_id = uuid.uuid4()
    MOCK_USERS[customer3_id] = UserInDB(
        id=customer3_id, email="inactive@example.com", first_name="Pasif", last_name="Kullanıcı", is_active=False, password_hash="fake-hashed-password-4"
    )

initialize_mock_users()

# ----------------------------------------------------------------------
# Yetkilendirme (Auth) Bağımlılıkları
# ----------------------------------------------------------------------

def get_current_admin_user() -> UserInDB:
    """Authorization başlığını kontrol ederek geçerli admin kullanıcısını döndürür."""
    admin_user = next((u for u in MOCK_USERS.values() if u.role_name == "admin"), None)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backend hatası: Mock admin kullanıcısı bulunamadı."
        )
    if admin_user.role_name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işleme erişim yetkiniz yok."
        )
    return admin_user


# ----------------------------------------------------------------------
# APIRouter Tanımlaması (ÖNEMLİ: /api/v1/admin öneki ile)
# ----------------------------------------------------------------------

admin_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["User Management (Admin)"],
    dependencies=[Depends(get_current_admin_user)],
)

# ----------------------------------------------------------------------
# 1. KULLANICI LİSTELEME VE ARAMA
# ----------------------------------------------------------------------
@admin_router.get(
    "/users",
    response_model=List[UserPublic],
    summary="1. Tüm Kullanıcıları Listele ve Ara"
)
def get_all_users(
    search: Optional[str] = Query(None, description="ID, Ad, Soyad veya E-posta ile arama yapın.")
):
    """Sistemdeki tüm kullanıcıları listeler veya arama sorgusuna göre filtreler."""
    initialize_mock_users() 
    users_list = list(MOCK_USERS.values())
    if search:
        search_lower = search.lower()
        users_list = [
            user for user in users_list
            if (search_lower in user.first_name.lower() or
                search_lower in user.last_name.lower() or
                search_lower in user.email.lower() or
                str(user.id).lower().startswith(search_lower))
        ]
    return [UserPublic.model_validate(user) for user in users_list]

# ----------------------------------------------------------------------
# 2. KULLANICI OLUŞTURMA
# ----------------------------------------------------------------------
@admin_router.post(
    "/users",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="2. Yeni Kullanıcı Oluşturma"
)
def create_user(user_data: UserCreateRequest):
    """Yeni bir kullanıcı hesabı oluşturur."""
    if any(user.email == user_data.email for user in MOCK_USERS.values()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu e-posta adresi zaten kullanılıyor."
        )

    # Parola hash'leme simülasyonu
    hashed_password = f"hashed_{user_data.password}"
    
    new_user = UserInDB(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password_hash=hashed_password
    )
    MOCK_USERS[new_user.id] = new_user
    
    return UserPublic.model_validate(new_user)

# ----------------------------------------------------------------------
# 3. KULLANICI BİLGİLERİNİ GÜNCELLEME
# ----------------------------------------------------------------------
@admin_router.patch(
    "/users/{user_id}",
    response_model=UserPublic,
    summary="3. Kullanıcı Bilgilerini Güncelleme (Ad/Soyad/E-posta)"
)
def update_user_info(
    user_id: uuid.UUID,
    user_update: UserUpdateRequest
):
    """Belirtilen ID'ye sahip kullanıcının bilgilerini (ad, soyad, e-posta) günceller."""
    user = MOCK_USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı.")
    
    # Sadece gönderilen alanları güncelle
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(user, key, value)
    
    MOCK_USERS[user_id] = user
    return UserPublic.model_validate(user)

# ----------------------------------------------------------------------
# 4. ROL VE YETKİ YÖNETİMİ
# ----------------------------------------------------------------------
@admin_router.patch(
    "/users/{user_id}/role",
    response_model=UserPublic,
    summary="4. Kullanıcı Rolünü Güncelle ('admin' veya 'customer')"
)
def update_user_role(
    user_id: uuid.UUID,
    role_update: UserUpdateRoleRequest
):
    """Belirtilen ID'ye sahip kullanıcının rolünü günceller."""
    user = MOCK_USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı.")
    
    new_role = role_update.new_role.lower()
    if new_role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz rol: '{role_update.new_role}'. Sadece {ALLOWED_ROLES} rolleri geçerlidir."
        )
    
    user.role_name = new_role
    MOCK_USERS[user_id] = user
    return UserPublic.model_validate(user)

# ----------------------------------------------------------------------
# 5a. KULLANICI HESABINI ASKIYA AL / AKTİFLEŞTİR
# ----------------------------------------------------------------------
@admin_router.patch(
    "/users/{user_id}/suspend",
    response_model=UserPublic,
    summary="5a. Kullanıcı Hesabını Askıya Al / Aktifleştir"
)
def suspend_user(user_id: uuid.UUID):
    """Belirtilen ID'ye sahip kullanıcının hesabının aktiflik durumunu tersine çevirir."""
    user = MOCK_USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı.")

    # Durumu tersine çevir
    user.is_active = not user.is_active
    MOCK_USERS[user_id] = user
    return UserPublic.model_validate(user)

# ----------------------------------------------------------------------
# 5b. KULLANICI HESABINI SİLME
# ----------------------------------------------------------------------
@admin_router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="5b. Kullanıcı Hesabını Kalıcı Olarak Silme"
)
def delete_user(user_id: uuid.UUID):
    """Belirtilen ID'ye sahip kullanıcıyı sistemden kalıcı olarak siler."""
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı.")
    
    del MOCK_USERS[user_id]
    return
