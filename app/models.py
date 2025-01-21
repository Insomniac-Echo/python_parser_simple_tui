from typing import Optional
from pydantic import BaseModel, Field

# Модели необходимо настроить под дроп в нужные таблицы и ячейки в бд
class Product(BaseModel):
    id_src: int
    name: str
    cashback: Optional[float] = None
    sale: Optional[int] = None
    brand: str
    rating: int
    supplier: str
    supplierRating: Optional[float] = None
    feedbacks: int
    reviewRating: float = Field(..., ge=0, le=5)
    promoTextCard: Optional[str] = None
    basic_price: int
    product_price: int
    total_price: int
    logistics_price: int
    return_price: int
    link: str
    img_url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[dict] = None
    on_stock: Optional[int] = None 
    count_sales: Optional[int] = None

class TrandsTable(BaseModel):
    id_src: int
    name: str
    rating: Optional[float] = None
    reviewRating: Optional[float] = None
    feedbacks: Optional[int] = None
    basic_price: Optional[int] = None
    product_price: Optional[int] = None
    total_price: Optional[int] = None
    count_sales: Optional[int] = None
    on_stock: Optional[int] = None
    link: Optional[str] = None
    img_link: Optional[str] = None

class CategoryTrandsTable(BaseModel):
    id_trands: int
    category_ru: str
    category_eng: str
    category_id: int
    parent_id: int