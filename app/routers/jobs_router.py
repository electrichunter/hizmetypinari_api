from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload
from typing import List

# Async için importlar eklendi
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select 

# Proje içi importlar
from ..models.job_models import Job
from ..models.user import User 
from ..schemas import job_schemas
from ..database import get_db
from .auth import get_current_user

router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["Jobs (İlanlar)"]
)

# DEĞİŞİKLİK: Endpoint birleştirildi ve akıllı hale getirildi.
@router.post("/", response_model=job_schemas.JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job( 
    job_data: job_schemas.JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Giriş yapan kullanıcı için veya (Admin/Provider ise) belirtilen müşteri için
    yeni bir iş ilanı oluşturur.
    """
    customer_id_to_assign = None
    role = current_user.role.role_name.value

    if role == 'customer':
        # Müşteri ise, ilanı kendi adına açar.
        customer_id_to_assign = current_user.id
    
    elif role in ['admin', 'provider']:
        # Admin/Provider ise, customer_id göndermesi zorunludur.
        if not job_data.customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{role}' rolüyle ilan oluşturmak için bir 'customer_id' göndermelisiniz."
            )
        
        # Gönderilen customer_id'nin geçerli bir müşteri olup olmadığını doğrula
        customer_user_result = await db.execute(select(User).where(User.id == job_data.customer_id))
        customer = customer_user_result.scalars().first()
        
        # Müşterinin rolünü de kontrol et
        if not customer:
             raise HTTPException(
                status_code=status.HTTP_44_NOT_FOUND,
                detail=f"ID'si {job_data.customer_id} olan bir kullanıcı bulunamadı."
            )
        
        # Gelen customer'ın rolünü yükle (Eğer user modelinde 'role' ilişkisi varsa)
        customer_role_result = await db.execute(
            select(User).options(joinedload(User.role)).where(User.id == job_data.customer_id)
        )
        customer_with_role = customer_role_result.scalars().first()

        if not customer_with_role or customer_with_role.role.role_name.value != 'customer':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID'si {job_data.customer_id} olan bir 'customer' bulunamadı."
            )
        
        customer_id_to_assign = job_data.customer_id

    # customer_id'yi Pydantic modelinden ayırarak Job objesini oluştur
    job_payload = job_data.model_dump(exclude={'customer_id'})
    new_job = Job(
        **job_payload,
        customer_id=customer_id_to_assign
    )
    
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    # Dönen yanıtın customer verisini yükle (JobResponse şeması için gerekli)
    await db.refresh(new_job, attribute_names=['customer'])
    return new_job

# DEĞİKLİK: /privileged-create endpoint'i silindi.

@router.get("/", response_model=List[job_schemas.JobListResponse])
async def get_all_jobs(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Sistemdeki tüm aktif ve açık ilanları listeler.
    """
    query = (
        select(Job)
        .options(joinedload(Job.service), joinedload(Job.district))
        .filter(Job.is_active == True, Job.status == 'open')
        .order_by(Job.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return jobs

@router.get("/{job_id}", response_model=job_schemas.JobResponse)
async def get_job_by_id(job_id: int, db: AsyncSession = Depends(get_db)):
    """
    Belirtilen ID'ye sahip ilanın detaylarını getirir.
    """
    query = (
        select(Job)
        .options(joinedload(Job.customer))
        .filter(Job.id == job_id)
    )
    job_result = await db.execute(query)
    job = job_result.scalars().first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID'si {job_id} olan bir ilan bulunamadı."
        )
    return job

