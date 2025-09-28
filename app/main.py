# ==============================================================================
# Gerekli Kütüphanelerin ve Modüllerin İçe Aktarılması (Imports)
# ==============================================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Proje içindeki kendi yönlendiricilerimizi (routers) import ediyoruz.
# Yönlendiriciler, API uç noktalarını mantıksal gruplara ayırmamızı sağlar.
from .routers.auth import auth_router
from .routers.jobs_router import router as jobs_router

# ==============================================================================
# FastAPI Uygulamasının Oluşturulması ve Yapılandırılması
# ==============================================================================
# FastAPI ana uygulama nesnesini oluşturuyoruz.
# title, description ve version gibi parametreler, otomatik oluşturulan
# API dokümantasyonunda (/docs) gösterilir.
app = FastAPI(
    title="Hizmet Pınarı API",
    description="Hizmet sağlayan ve arayan kullanıcılar için geliştirilmiş bir platform.",
    version="1.0.0",
    # Dokümantasyon URL'lerini özelleştirebiliriz.
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==============================================================================
# CORS (Cross-Origin Resource Sharing) Yapılandırması
# ==============================================================================
# Tarayıcı güvenlik politikaları gereği, frontend (örn: http://localhost:3000)
# ve backend (örn: http://127.0.0.1:8000) farklı adreslerde çalıştığında
# doğrudan iletişime izin verilmez. CORS Middleware, bu iletişime izin
# vermemizi sağlayan bir mekanizmadır.

# Frontend uygulamasının çalışacağı adresleri bir listeye ekliyoruz.
# Güvenlik için sadece belirli adreslere izin vermek en iyi pratiktir.
allowed_origins = [
    "http://localhost:3000",
]

# Middleware'i FastAPI uygulamasına ekliyoruz.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Sadece listedeki adreslerden gelen isteklere izin ver.
    allow_credentials=True,       # Kimlik bilgileri (cookie vb.) içeren isteklere izin ver.
    allow_methods=["*"],          # Tüm HTTP metodlarına (GET, POST, PUT, DELETE vb.) izin ver.
    allow_headers=["*"],          # Tüm HTTP başlıklarına izin ver.
)

# ==============================================================================
# API Yönlendiricilerinin (Routers) Uygulamaya Dahil Edilmesi
# ==============================================================================
# Farklı dosyalarda tanımladığımız API uç noktası gruplarını (router'ları)
# ana uygulamaya dahil ediyoruz. Bu, projenin modüler ve düzenli kalmasını sağlar.

# Kimlik doğrulama (Authentication) ile ilgili uç noktaları ekliyoruz.
# prefix: Bu router'daki tüm yolların başına '/api/v1/auth' eklenir.
# tags: /docs sayfasında bu uç noktaları "Authentication" başlığı altında gruplar.
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

# İlanlar (Jobs) ile ilgili uç noktaları ekliyoruz.
# Bu router'daki yollar kendi içinde tanımlandığı için (prefix="/api/v1/jobs"),
# burada tekrar belirtmemize gerek yok.
app.include_router(jobs_router, tags=["Jobs (İlanlar)"])


# ==============================================================================
# Kök (Root) Uç Noktası
# ==============================================================================
# API'nin çalışıp çalışmadığını kontrol etmek için basit bir test uç noktası.
# Tarayıcıda http://127.0.0.1:8000 adresine gidildiğinde bu mesaj görünür.
@app.get("/", tags=["Root"])
def read_root():
    """
    API'nin ana giriş noktası. Hoş geldiniz mesajı döndürür.
    """
    return {"message": "Hizmet Pınarı API'sine Hoş Geldiniz!"}

