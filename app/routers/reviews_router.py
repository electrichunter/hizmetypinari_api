    
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List

# Proje içi importlar
from ..database import get_db
from ..models.user import User
from ..models.job_models import Job, Offer, JobStatus
from ..models.review_models import Review # Review modelini import et
from ..schemas import review_schema
from .auth import get_current_user

reviews_router = APIRouter(
    prefix="/api/v1",
    tags=["Reviews (Değerlendirmeler)"]
)

@reviews_router.post("/jobs/{job_id}/reviews", response_model=review_schema.Review, status_code=status.HTTP_201_CREATED)
async def create_review_for_job(
    job_id: int,
    review_data: review_schema.ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Müşterinin, tamamlanmış bir iş (job) için hizmet sağlayıcıya (provider) yorum ve puan bırakmasını sağlar.
    Sadece ilanın sahibi (customer) tarafından çağrılabilir.
    """
    # 1. Sadece 'customer' rolündekiler yorum yapabilir
    if current_user.role.role_name.value != 'customer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yalnızca 'customer' rolündeki kullanıcılar yorum yapabilir."
        )

    # 2. İlanı (Job) bul ve ilişkili teklifi (accepted olanı) yükle
    job = await db.get(Job, job_id, options=[joinedload(Job.offers)])
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="İlan bulunamadı.")

    # 3. Güvenlik Kontrolü: İlan, giriş yapan kullanıcıya mı ait?
    if job.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yalnızca kendi ilanınıza yorum yapabilirsiniz."
        )

    # 4. İlanın durumunu kontrol et ('completed' olmalı)
    if job.status != JobStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bu ilan '{job.status.value}' durumunda. Yalnızca 'completed' durumundaki ilanlara yorum yapılabilir."
        )

    # 5. İlan için daha önce yorum yapılmış mı kontrol et
    existing_review = (await db.execute(
        select(Review).where(Review.job_id == job_id)
    )).scalar_one_or_none()

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu ilan için zaten bir yorum yapılmış."
        )

    # 6. Yeni yorumu oluştur
    new_review = Review(
        **review_data.model_dump(),
        job_id=job_id,
        customer_id=current_user.id # Yorumu yapan müşteri
    )
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)

    return new_review