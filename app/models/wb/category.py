from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import registry

mapper_registry = registry()

# Таблица category_trands
class CategoryTrandsTable:
    __tablename__ = 'category_trands'
    id_category = Column(Integer, primary_key=True, autoincrement=True)
    id_trands = Column(Integer, ForeignKey('trands.id_src'))
    category_ru = Column(String(500), nullable=True)
    category_eng = Column(String(500), nullable=True)
    podcat_1_ru = Column(String(500), nullable=True)
    podcat_1_eng = Column(String(500), nullable=True)
    podcat_2_ru = Column(String(500), nullable=True)
    podcat_2_eng = Column(String(500), nullable=True)
    podcat_3_ru = Column(String(500), nullable=True)
    podcat_3_eng = Column(String(500), nullable=True)
    podcat_4_ru = Column(String(500), nullable=True)
    podcat_4_eng = Column(String(500), nullable=True)
    podcat_5_ru = Column(String(500), nullable=True)
    podcat_5_eng = Column(String(500), nullable=True)

    __table_args__ = (
        Index('idx_category_trands_id_trands', 'id_trands'),
        Index('idx_category_trands_category_eng', 'category_eng'),
    )
