from sqlalchemy import Integer, Float, TIMESTAMP, VARCHAR, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.wb.base import Base

class TrandsTable(Base):
    __tablename__ = 'trands'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_src: Mapped[int] = mapped_column(index=True, comment="id на WB")
    name: Mapped[str] = mapped_column(VARCHAR(250))
    rating: Mapped[float] = mapped_column(Float)
    reviewRating: Mapped[float] = mapped_column(Float)
    feedbacks: Mapped[int] = mapped_column(Integer)
    basic_price: Mapped[int] = mapped_column(Integer)
    product_price: Mapped[int] = mapped_column(Integer)
    total_price: Mapped[int] = mapped_column(Integer)
    count_sales: Mapped[int] = mapped_column(Integer, comment="число продаж")
    on_stock: Mapped[int] = mapped_column(Integer, comment="остаток на складе")
    link: Mapped[str] = mapped_column(VARCHAR(384), comment="ссылка на товар на ВБ")
    img_link: Mapped[str] = mapped_column(VARCHAR(512), comment="ссылка на картинку на ВБ")
    
    # Поля категорий (5 уровней)
    category_ru: Mapped[str] = mapped_column(VARCHAR(250), nullable=False)
    category_eng: Mapped[str] = mapped_column(VARCHAR(120), nullable=False)
    podcat_1_ru: Mapped[str] = mapped_column(VARCHAR(250), nullable=False)
    podcat_1_eng: Mapped[str] = mapped_column(VARCHAR(150), nullable=False)
    podcat_2_ru: Mapped[str] = mapped_column(VARCHAR(250), nullable=False)
    podcat_2_eng: Mapped[str] = mapped_column(VARCHAR(150), nullable=False)
    Date_tmst: Mapped[str] = mapped_column(TIMESTAMP ,server_default=func.now())
    
    # Индексы в таблице
    
    __table_args__ = (
        Index('idx_id_src', id_src),
        Index('idx_name', name, mysql_length=50,),
        Index('idx_id_src_date', id_src, Date_tmst),
        Index('idx_sales_date', count_sales, Date_tmst),
        Index('idx_date_id_src', Date_tmst, id_src),
        Index('idx_stock_sales', on_stock, count_sales),
        Index('idx_src_sales_date', id_src, count_sales, Date_tmst),
        Index('idx_full_category', category_eng, podcat_1_eng, podcat_2_eng, mysql_length=50)
    )
