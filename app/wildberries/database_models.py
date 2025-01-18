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
    date_of = Column(TIMESTAMP)

# Таблица trands_info
class TrandsInfoTable(Base):
    __tablename__ = 'trands_info'
    id_info = Column(Integer, primary_key=True, autoincrement=True)
    id_trands = Column(Integer, ForeignKey('trands.id_src'))
    name = Column(String(500))
    brand = Column(String(500))
    cashback = Column(String(5))
    sale = Column(String(5))
    link = Column(Text)
    img_link = Column(Text)
    __table_args__ = (Index('name', 'name'),)

# Таблица category_trands
class CategoryTrandsTable(Base):
    __tablename__ = 'category_trands'
    id_category = Column(Integer, primary_key=True, autoincrement=True)
    id_trands = Column(Integer, ForeignKey('trands.id_src'))
    category_ru = Column(String(500))
    category_eng = Column(String(500), index=True)
    category_id = Column(Integer)
    parent_id = Column(Integer)
    __table_args__ = (Index('id_trands', 'id_trands'), Index('category_eng', 'category_eng'),)