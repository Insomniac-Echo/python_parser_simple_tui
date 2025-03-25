from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey, Index, String

from app.models.wb.base import Base

# Таблица category_trands
class CategoryTrandsTable(Base):
    __tablename__ = 'category_trands'
    
    id_category: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_trands: Mapped[int] = mapped_column(ForeignKey('trands.id_src'))
    category_ru: Mapped[str] = mapped_column(String(255), nullable=True)
    category_eng: Mapped[str] = mapped_column(String(255), nullable=True)
    podcat_1_ru: Mapped[str] = mapped_column(String(255), nullable=True)
    podcat_1_eng: Mapped[str] = mapped_column(String(255), nullable=True)
    podcat_2_ru: Mapped[str] = mapped_column(String(255), nullable=True)
    podcat_2_eng: Mapped[str] = mapped_column(String(255), nullable=True)
    podcat_3_ru: Mapped[str] = mapped_column(String(255), nullable=True)
    podcat_3_eng: Mapped[str] = mapped_column(String(255), nullable=True)
    podcat_4_ru: Mapped[str] = mapped_column(String(255), nullable=True)
    podcat_4_eng: Mapped[str] = mapped_column(String(255), nullable=True)
    podcat_5_ru: Mapped[str] = mapped_column(String(255), nullable=True)
    podcat_5_eng: Mapped[str] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        Index('idx_category_trands_id_trands', 'id_trands'),
        Index('idx_category_trands_category_eng', 'category_eng'),
    )
