from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base # .. ile bir üst dizindeki 'database' dosyasını içe aktarıyoruz.
import enum

# SQL şemasındaki 'roles' tablosunun Enum tipini tanımlıyoruz.
class RoleName(enum.Enum):
    admin = "admin"
    provider = "provider"
    customer = "customer"

# SQLAlchemy için 'roles' tablosu modeli.
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(Enum(RoleName), unique=True, index=True, nullable=False)
    description = Column(String(255))
    
    # Kullanıcılar ile ilişki kuruyoruz.
    users = relationship("User", back_populates="role")

# SQLAlchemy için 'users' tablosu modeli.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # 'roles' tablosuyla ilişki kuruyoruz.
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users")
