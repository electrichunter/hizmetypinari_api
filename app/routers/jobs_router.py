from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

# Proje içi importlar
from ..models.job_models import Job
from ..models.user import User 
from ..schemas import job_schemas
from ..database import get_db
from .auth import get_current_user

# YENİ ŞEMA: Admin veya provider'ın müşteri adına ilan oluşturması için.
# Bu şema, normal ilan oluşturma şemasına ek olarak 'customer_id' alanı içerir.
class JobCreateByPrivileged(job_schemas.JobCreate):
    customer_id: int

router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["Jobs (İlanlar)"]
)

# MEVCUT UÇ NOKTA: Sadece müşterilerin kendileri için ilan oluşturması.
@router.post("/", response_model=job_schemas.JobResponse, status_code=status.HTTP_201_CREATED)
def create_job_for_customer(
    job_data: job_schemas.JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mevcut müşterinin kendisi için yeni bir iş ilanı oluşturmasını sağlar.
    """
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
    db.commit()
    db.refresh(new_job)

    return new_job

# YENİ UÇ NOKTA: Admin ve Provider'ların müşteri adına ilan oluşturması.
@router.post("/privileged-create", response_model=job_schemas.JobResponse, status_code=status.HTTP_201_CREATED)
def create_job_by_privileged_user(
    job_data: JobCreateByPrivileged,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin veya Provider rolündeki kullanıcıların, belirli bir müşteri adına yeni bir iş ilanı oluşturmasını sağlar.
    """
    # 1. Yetki kontrolü: Sadece admin ve provider bu işlemi yapabilir.
    allowed_roles = ['admin', 'provider']
    if current_user.role.role_name.value not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlemi yalnızca 'admin' veya 'provider' rolündeki kullanıcılar yapabilir."
        )

    # 2. Müşteri kontrolü: Gönderilen customer_id'nin geçerli bir müşteri olup olmadığını doğrula.
    customer_user = db.query(User).filter(User.id == job_data.customer_id).first()
    if not customer_user or customer_user.role.role_name.value != 'customer':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID'si {job_data.customer_id} olan bir müşteri bulunamadı."
        )

    # 3. İlanı oluştur. customer_id'yi modelden çıkarıp ayrıca ekliyoruz.
    new_job = Job(
        **job_data.model_dump(exclude={'customer_id'}),
        customer_id=job_data.customer_id
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.get("/", response_model=List[job_schemas.JobListResponse])
def get_all_jobs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Sistemdeki tüm aktif ve açık ilanları listeler.
    """
    jobs = (
        db.query(Job)
        .options(joinedload(Job.service), joinedload(Job.district))
        .filter(Job.is_active == True, Job.status == 'open')
        .order_by(Job.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return jobs

@router.get("/{job_id}", response_model=job_schemas.JobResponse)
def get_job_by_id(job_id: int, db: Session = Depends(get_db)):
    """
    Belirtilen ID'ye sahip ilanın detaylarını getirir.
    """
    job = (
        db.query(Job)
        .options(joinedload(Job.customer))
        .filter(Job.id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID'si {job_id} olan bir ilan bulunamadı."
        )
    return job

