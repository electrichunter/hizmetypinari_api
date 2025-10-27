from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List

# Proje içi importlar
from ..database import get_db
from ..models.user import User
from ..models.job_models import Job, Offer, Provider, JobStatus
from ..schemas import offer_schemas
from .auth import get_current_user

router = APIRouter(
    prefix="/api/v1",  # Ana prefix'i burada tutuyoruz
    tags=["Offers (Teklifler)"]
)

@router.post("/jobs/{job_id}/offers", response_model=offer_schemas.OfferResponse, status_code=status.HTTP_201_CREATED)
async def create_offer_for_job(
    job_id: int,
    offer_data: offer_schemas.OfferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Giriş yapmış 'provider' rolündeki kullanıcının,
    belirtilen bir ilana (job) teklif vermesini sağlar.
    """
    
    # 1. Sadece 'provider' rolündekiler teklif verebilir
    if current_user.role.role_name.value != 'provider':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yalnızca 'provider' rolündeki kullanıcılar teklif verebilir."
        )

    # 2. İlanı (Job) bul
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="İlan bulunamadı.")

    # 3. İlanın durumunu kontrol et ('open' değilse teklif verilemez)
    if job.status != JobStatus.open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bu ilan '{job.status.value}' durumunda. Yalnızca 'open' durumundaki ilanlara teklif verilebilir."
        )
        
    # 4. Provider kendi ilanına teklif veremez
    if job.customer_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kendi açtığınız ilana teklif veremezsiniz."
        )

    # 5. Provider'ın profilini bul veya oluştur (ÇOK ÖNEMLİ)
    # provider_profile, 'providers' tablosundaki kayıttır.
    provider_profile = (await db.execute(
        select(Provider).where(Provider.user_id == current_user.id)
    )).scalar_one_or_none()

    if not provider_profile:
        # Eğer 'provider' rolüyle kayıt olunmuş ama 'providers' tablosunda
        # profili henüz oluşmamışsa, burada otomatik oluştur.
        provider_profile = Provider(
            user_id=current_user.id,
            business_name=f"{current_user.first_name} {current_user.last_name}" # Varsayılan iş adı
        )
        db.add(provider_profile)
        await db.flush() # ID'sini almak için veritabanına anlık gönder

    # 6. Provider bu ilana daha önce teklif vermiş mi?
    existing_offer = (await db.execute(
        select(Offer).where(
            Offer.job_id == job_id,
            Offer.provider_id == provider_profile.id
        )
    )).scalar_one_or_none()

    if existing_offer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu ilana zaten bir teklif vermişsiniz."
        )

    # 7. Yeni teklifi oluştur
    new_offer = Offer(
        **offer_data.model_dump(),
        job_id=job_id,
        provider_id=provider_profile.id  # 'user.id' DEĞİL, 'provider.id'
    )
    db.add(new_offer)
    await db.commit()
    
    # 8. Yanıt için verileri ilişkilerle birlikte yükle
    await db.refresh(new_offer, attribute_names=["provider"])

    return new_offer


@router.get("/jobs/{job_id}/offers", response_model=List[offer_schemas.OfferResponse])
async def get_offers_for_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Giriş yapmış 'customer' (müşteri) rolündeki kullanıcının,
    KENDİSİNE ait bir ilana gelen tüm teklifleri listelemesini sağlar.
    """
    
    # 1. İlanı (Job) bul
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="İlan bulunamadı.")
        
    # 2. Güvenlik Kontrolü: İlan, giriş yapan kullanıcıya mı ait?
    if job.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yalnızca kendi ilanınıza gelen teklifleri görebilirsiniz."
        )
        
    # 3. İlana ait teklifleri, provider bilgileriyle birlikte çek
    query = (
        select(Offer)
        .options(joinedload(Offer.provider))
        .where(Offer.job_id == job_id)
        .order_by(Offer.offer_price.asc()) # En düşük tekliften sırala
    )
    
    result = await db.execute(query)
    offers = result.scalars().all()
    
    return offers
