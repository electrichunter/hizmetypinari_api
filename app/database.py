import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Ortam değişkenlerini .env dosyasından yükle
load_dotenv()

# Ortam değişkenlerinden veritabanı URL'sini alıyoruz.
DATABASE_URL = os.getenv("DATABASE_URL")

# Asenkron veritabanı motorunu oluşturuyoruz.
# Echo=True, veritabanı işlemlerini konsola yazdırır, bu hata ayıklama için yararlıdır.
engine = create_async_engine(DATABASE_URL, echo=True)

# Oturum (session) için bir fabrika oluşturuyoruz.
# AsyncSession, SQLAlchemy'nin asenkron işlemler için sunduğu bir özelliktir.
AsyncSessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# SQLAlchemy ORM için temel sınıf. Modellerimiz bu sınıftan türetilecek.
Base = declarative_base()

# Bağımlılık enjeksiyonu için bir fonksiyon.
# Her istek için bir veritabanı oturumu sağlar.
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
# Oturumu kapatır ve kaynakları serbest bırakır.    