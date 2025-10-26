from fastapi import APIRouter, Depends, HTTPException, status
# SENKRON 'Session' importunu kaldırıyoruz
from sqlalchemy.orm import joinedload 
from typing import List

# ASENKRON 'AsyncSession' ve 'select' importları (bunları eklemiştiniz, kalmalı)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select 

# Proje içi importlar
from ..models.job_models import Job
from ..models.user import User 
from ..schemas import job_schemas
from ..database import get_db
from .auth import get_current_user # get_current_user zaten async

# YENİ ŞEMA: Admin veya provider'ın müşteri adına ilan oluşturması için.
class JobCreateByPrivileged(job_schemas.JobCreate):
    customer_id: int

router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["Jobs (İlanlar)"]
)

# MEVCUT UÇ NOKTA: Sadece müşterilerin kendileri için ilan oluşturması.
# 'def' -> 'async def'
# 'db: Session' -> 'db: AsyncSession'
@router.post("/", response_model=job_schemas.JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job_for_customer(
    job_data: job_schemas.JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mevcut müşterinin kendisi için yeni bir iş ilanı oluşturmasını sağlar.
    """
    # Yetki kontrolü (Bu kısım aynı kalır)
    if current_user.role.role_name.value != 'customer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu uç nokta yalnızca 'customer' rolündeki kullanıcılar içindir. Admin veya provider iseniz lütfen /privileged-create uç noktasını kullanın."
        )

    new_job = Job(
        **job_data.model_dump(),
        customer_id=current_user.id
    )
    db.add(new_job)
    
    # 'db.commit()' -> 'await db.commit()'
    await db.commit()
    # 'db.refresh()' -> 'await db.refresh()'
    await db.refresh(new_job)

    return new_job

# YENİ UÇ NOKTA: Admin ve Provider'ların müşteri adına ilan oluşturması.
# 'def' -> 'async def'
# 'db: Session' -> 'db: AsyncSession'
@router.post("/privileged-create", response_model=job_schemas.JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job_by_privileged_user(
    job_data: JobCreateByPrivileged,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin veya Provider rolündeki kullanıcıların, belirli bir müşteri adına yeni bir iş ilanı oluşturmasını sağlar.
    """
    # 1. Yetki kontrolü (Aynı kalır)
    allowed_roles = ['admin', 'provider']
    if current_user.role.role_name.value not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlemi yalnızca 'admin' veya 'provider' rolündeki kullanıcılar yapabilir."
        )

    # 2. Müşteri kontrolü: 'db.query' -> 'await db.execute(select(...))'
    customer_query = select(User).options(joinedload(User.role)).filter(User.id == job_data.customer_id)
    result = await db.execute(customer_query)
    customer_user = result.scalars().first()
    
    if not customer_user or customer_user.role.role_name.value != 'customer':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID'si {job_data.customer_id} olan bir müşteri bulunamadı."
        )

    # 3. İlanı oluştur.
    new_job = Job(
        **job_data.model_dump(exclude={'customer_id'}),
        customer_id=job_data.customer_id
    )
    db.add(new_job)
    
    # 'db.commit()' -> 'await db.commit()'
    await db.commit()
    # 'db.refresh()' -> 'await db.refresh()'
    await db.refresh(new_job)
    
    return new_job

# 'def' -> 'async def'
# 'db: Session' -> 'db: AsyncSession'
@router.get("/", response_model=List[job_schemas.JobListResponse])
async def get_all_jobs(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Sistemdeki tüm aktif ve açık ilanları listeler.
    """
    # 'db.query(Job)' -> 'select(Job)'
    query = (
        select(Job)
        .options(joinedload(Job.service), joinedload(Job.district))
        .filter(Job.is_active == True, Job.status == 'open')
        .order_by(Job.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    # Sorguyu 'await db.execute()' ile çalıştır
    result = await db.execute(query)
    # Sonuçları '.scalars().all()' ile al
    jobs = result.scalars().all()
    
    return jobs

# 'def' -> 'async def'
# 'db: Session' -> 'db: AsyncSession'
@router.get("/{job_id}", response_model=job_schemas.JobResponse)
async def get_job_by_id(job_id: int, db: AsyncSession = Depends(get_db)):
    """
    Belirtilen ID'ye sahip ilanın detaylarını getirir.
    """
    # 'db.query(Job)' -> 'select(Job)'
    query = (
        select(Job)
        .options(joinedload(Job.customer))
        .filter(Job.id == job_id)
    )
    
    # Sorguyu 'await db.execute()' ile çalıştır
    result = await db.execute(query)
    # Tek bir sonuç için '.scalars().first()' kullan
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID'si {job_id} olan bir ilan bulunamadı."
        )
    return job
