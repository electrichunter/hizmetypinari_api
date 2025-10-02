# ==============================================================================
# Gerekli Kütüphanelerin ve Modüllerin İçe Aktarılması (Imports)
# ==============================================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging 

# Proje içindeki yönlendiricileri (routers) import ediyoruz.
# Bu router'ların kendi içinde tam öneklerini (/api/v1/...) taşıdığını varsayıyoruz.
from .routers.auth import auth_router 
from .routers.jobs_router import router as jobs_router 
from .routers.admin_router import admin_router 

# Logging ayarını ekleyelim.
logging.basicConfig(level=logging.INFO)

# ==============================================================================
# FastAPI Uygulamasının Oluşturulması ve Yapılandırılması
# ==============================================================================
# FastAPI ana uygulama nesnesini oluşturuyoruz.
app = FastAPI(
  title="Hizmet Pınarı API",
  description="Hizmet sağlayan ve arayan kullanıcılar için geliştirilmiş bir platform.",
  version="1.0.0",
  docs_url="/docs",
  redoc_url="/redoc"
)

# ==============================================================================
# CORS (Cross-Origin Resource Sharing) Yapılandırması
# ==============================================================================
# Frontend uygulamasının çalışacağı adreslere izin veriyoruz.
allowed_origins = [
  "http://localhost:3000", # React uygulamanızın adresi
    "http://127.0.0.1:3000",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=allowed_origins,
  allow_credentials=True,     
  allow_methods=["*"],      
  allow_headers=["*"],      
)

# ==============================================================================
# API Yönlendiricilerinin (Routers) Uygulamaya Dahil Edilmesi
# ==============================================================================
# Router'lar kendi dosyalarında tam öneklerini taşıdığından, burada 'prefix' parametresini kullanmıyoruz.
app.include_router(auth_router, tags=["Authentication"]) 
app.include_router(jobs_router, tags=["Jobs (İlanlar)"]) 
app.include_router(admin_router, tags=["User Management (Admin)"]) 


# ==============================================================================
# Kök (Root) Uç Noktası
# ==============================================================================
@app.get("/", tags=["Root"])
def read_root():
  """
  API'nin ana giriş noktası. Hoş geldiniz mesajı döndürür.
  """
  return {"message": "Hizmet Pınarı API'sine Hoş Geldiniz!"}
