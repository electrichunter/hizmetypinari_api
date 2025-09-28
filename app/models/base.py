# models/base.py

# Bu dosya, tüm SQLAlchemy modellerinin miras alacağı temel Base sınıfını tanımlar.
# Bu merkezi yapı, modeller arasında döngüsel bağımlılık (circular import)
# sorunlarının önüne geçer ve veritabanı meta verilerini tek bir yerde toplar.

from sqlalchemy.orm import declarative_base

# Tüm modellerimiz bu Base sınıfından türeyecektir.
Base = declarative_base()

