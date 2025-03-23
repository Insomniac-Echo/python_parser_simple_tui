from sqlalchemy import Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.models.wb.base import Base

# Таблица trands
class TrandsTable(Base):
    __tablename__ = 'trands'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_src: Mapped[int] = mapped_column( index=True)
    name: Mapped[str]
    rating: Mapped[float]
    reviewRating: Mapped[float]
    feedbacks: Mapped[int]
    basic_price: Mapped[int]
    product_price: Mapped[int]
    total_price: Mapped[int]
    count_sales: Mapped[int]
    on_stock: Mapped[int]
    link: Mapped[str] = mapped_column(Text)
    img_link: Mapped[str] = mapped_column(Text)
    date_of: Mapped[str] = mapped_column(TIMESTAMP)
    Date_tmst: Mapped[str] = mapped_column(TIMESTAMP ,server_default=func.now())
