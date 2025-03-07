from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP, func
from sqlalchemy.orm import registry

mapper_registry = registry()

# Таблица trands
class TrandsTable:
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
    Date_tmst = Column(
        TIMESTAMP, 
        server_default=func.now()
    )
