from sqlalchemy import Column, Integer, String, TIMESTAMP, JSON, Text, VARCHAR, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.wb.base import Base

class TrandsTable(Base):
    __tablename__ = 'trands'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_src: Mapped[int] = mapped_column(index=True, comment="id на WB")
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

    # Данные из get_product_info
    size_on_model: Mapped[str] = mapped_column(String(100))  # Из get_product_info
    model_parameters: Mapped[str] = mapped_column(String(255))  # Из get_product_info

    # JSON-поля для вложенных данных
    sizes_table: Mapped[dict] = mapped_column(JSON)  # Хранит список размеров и их параметров
    reviews_data: Mapped[dict] = mapped_column(JSON)  # Хранит отзывы и проценты соответствия