from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from ..database import get_db
from ..models.user import User, Role, RoleName
from ..schemas.user_schema import UserCreate, UserResponse, UserLogin, Token

# Şifre hashleme için CryptContext objesi oluşturulur. Artık Argon2 kullanılıyor.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# FastAPI için bir yönlendirici (router) oluşturulur.
auth_router = APIRouter()

# Ortam değişkenlerinden SECRET_KEY, ALGORITHM ve ACCESS_TOKEN_EXPIRE_MINUTES alınır.
SECRET_KEY = "sizin-cok-gizli-anahtariniz"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2PasswordBearer, token'ı almamızı sağlar.
# Bu sınıf, tokenUrl parametresini kullanarak JWT'nin nereden alınacağını belirtir.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Şifreyi hashlemek için yardımcı fonksiyon.
def get_password_hash(password: str) -> str:
    """Hashes a password using the configured scheme (Argon2)."""
    return pwd_context.hash(password)

# Şifreyi doğrulamak için yardımcı fonksiyon.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

# JWT token oluşturmak için yardımcı fonksiyon.
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Yeni bir kullanıcı kaydı oluşturur.
@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Yeni bir kullanıcı kaydı oluşturur.
    """
    # 1. E-posta adresinin zaten kullanımda olup olmadığını kontrol et.
    existing_user = await db.execute(select(User).where(User.email == user_data.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta adresi zaten kayıtlı."
        )

    # 2. Kullanıcının rolünü (örn: customer) veritabanından bul.
    # Bu adım, veritabanı şemasının istediği 'role_id'yi bulmak için zorunludur.
    role_obj = await db.execute(select(Role).where(Role.role_name == user_data.role_name))
    role = role_obj.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Belirtilen rol adı '{user_data.role_name}' bulunamadı."
        )

    # 3. Şifreyi güvenli bir şekilde hashle.
    hashed_password = get_password_hash(user_data.password)

    # 4. Yeni kullanıcı objesini oluştur. Artık role_id'yi kullanabiliriz.
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role_id=role.id,  # Veritabanının istediği 'role_id'yi atıyoruz.
        is_active=True
    )

    # 5. Kullanıcıyı veritabanına ekle ve değişikliği kaydet.
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "Kullanıcı başarıyla kaydedildi."}

# Giriş rotası. Kullanıcı giriş yapar ve bir JWT token alır.
# Artık JSON body kullanıyor.
@auth_router.post("/login", response_model=Token)
async def login_for_access_token(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    # Kullanıcıyı ve ilişkili rolünü tek bir sorguda getir.
    query = select(User).options(selectinload(User.role)).where(User.email == user_data.email)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        # Rol adını user objesinin ilişkili rolünden alıp stringe çeviriyoruz.
        data={"sub": user.email, "role": user.role.role_name.value},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Mevcut kullanıcıyı almak için yardımcı fonksiyon.
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role_name: RoleName = payload.get("role")
        if email is None:
            raise credentials_exception
        token_data = {"email": email, "role": role_name}
    except JWTError:
        raise credentials_exception
    
    # Kullanıcıyı ve ilişkili rolünü tek bir sorguda getir.
    user_query = select(User).options(selectinload(User.role)).where(User.email == token_data["email"])
    user_result = await db.execute(user_query)
    user = user_result.scalars().first()
    
    if user is None:
        raise credentials_exception
    
    # Kullanıcı objesine, ilişkili role_name özelliğini ekle.
    user.role_name = user.role.role_name
    
    return user

# Kullanıcıya özel hoş geldin mesajı veren korumalı rota.
@auth_router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

