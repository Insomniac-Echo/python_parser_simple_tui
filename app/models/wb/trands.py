from sqlalchemy import Column, Integer, Float, Text, TIMESTAMP, VARCHAR, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.wb.base import Base

class TrandsTable(Base):
    __tablename__ = 'trands'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_src: Mapped[int] = mapped_column(index=True, comment="id на WB")
    name: Mapped[str] = mapped_column(VARCHAR(700))
    rating: Mapped[float] = mapped_column(Float)
    reviewRating: Mapped[float] = mapped_column(Float)
    feedbacks: Mapped[int] = mapped_column(Integer)
    basic_price: Mapped[int] = mapped_column(Integer)
    product_price: Mapped[int] = mapped_column(Integer)
    total_price: Mapped[int] = mapped_column(Integer)
    count_sales: Mapped[int] = mapped_column(Integer, comment="число продаж")
    on_stock: Mapped[int] = mapped_column(Integer, comment="остаток на складе")
    link: Mapped[str] = mapped_column(Text, comment="ссылка на товар на ВБ")
    img_link: Mapped[str] = mapped_column(Text, comment="ссылка на картинку на ВБ")
    
    # Поля категорий (5 уровней)
    category_ru: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    category_eng: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    podcat_1_ru: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    podcat_1_eng: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    podcat_2_ru: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    podcat_2_eng: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    podcat_3_ru: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    podcat_3_eng: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    podcat_4_ru: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    podcat_4_eng: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    podcat_5_ru: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    podcat_5_eng: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    
    Date_tmst: Mapped[str] = mapped_column(TIMESTAMP ,server_default=func.now())


    __table_args__ = (
        Index('idx_id_src', 'id_src'),
    )