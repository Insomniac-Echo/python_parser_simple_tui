from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Таблица trands
class TrandsTable(Base):
    __tablename__ = 'trands'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_src = Column(Integer)
    rating = Column(Float)
    reviewRating = Column(Float)
    feedbacks = Column(Integer)
    basic_price = Column(Integer)
    product_price = Column(Integer)
    total_price = Column(Integer)
    count_sales = Column(Integer)
    on_stock = Column(Integer)
    date_of = Column(TIMESTAMP)

# Таблица trands_info
class TrandsInfoTable(Base):
    __tablename__ = 'trands_info'
    id_info = Column(Integer, primary_key=True, autoincrement=True)
    id_trands = Column(Integer, ForeignKey('trands.id'))
    name = Column(String(500))
    brand = Column(String(500))
    cashback = Column(String(5))
    sale = Column(String(5))
    link = Column(Text)
    img_link = Column(Text)

# Таблица category_trands
class CategoryTrandsTable(Base):
    __tablename__ = 'category_trands'
    id_category = Column(Integer, primary_key=True, autoincrement=True)
    id_trands = Column(Integer, ForeignKey('trands.id'))
    category_ru = Column(String(500))
    category_eng = Column(String(500))
    category_id = Column(Integer)
    parent_id = Column(Integer)
