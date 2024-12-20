from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Пересмотреть типы данных на соответствие с теми, что мы получаем из функций
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

# Таблица products
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_src = Column(Integer, unique=True)
    name = Column(String(500))
    cashback = Column(Float)
    sale = Column(Integer)
    brand = Column(String(500))
    rating = Column(Integer)
    supplier = Column(String(500))
    supplierRating = Column(Float)
    feedbacks = Column(Integer)
    reviewRating = Column(Float)
    promoTextCard = Column(Text)
    basic_price = Column(Integer)
    product_price = Column(Integer)
    total_price = Column(Integer)
    logistics_price = Column(Integer)
    return_price = Column(Integer)
    link = Column(Text)
    img_link = Column(Text)
    description = Column(Text)
    category_ru = Column(String(500))
    category_eng = Column(String(500))
    category_id = Column(Integer)
    parent_id = Column(Integer)