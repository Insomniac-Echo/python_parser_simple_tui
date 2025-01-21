from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, TIMESTAMP, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# Таблица trands
class TrandsTable(Base):
    __tablename__ = 'trands'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_src = Column(Integer, index=True)
    name = Column(String(500))
    rating = Column(Float)
    reviewRating = Column(Float)
    feedbacks = Column(Integer)
    basic_price = Column(Integer)
    product_price = Column(Integer)
    total_price = Column(Integer)
    count_sales = Column(Integer)
    on_stock = Column(Integer)
    link = Column(Text)
    img_link = Column(Text)
    date_of = Column(TIMESTAMP)

# Таблица category_trands
class CategoryTrandsTable(Base):
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