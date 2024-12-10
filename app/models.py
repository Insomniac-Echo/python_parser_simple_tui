from typing import Optional
from pydantic import BaseModel, Field

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

class TrandsTable(BaseModel):
    id_src: Optional[int]
    rating: Optional[float]
    reviewRating: Optional[float]
    feedbacks: Optional[int]
    basic_price: Optional[int]
    product_price: Optional[int]
    total_price: Optional[int]
    count_sales: Optional[int]
    on_stock: Optional[int]

class TrandsInfoTable(BaseModel):
    id_trands: int
    name: Optional[str]
    brand: Optional[str]
    cashback: Optional[str]
    sale: Optional[str]
    link: Optional[str]
    img_link: Optional[str]

class CategoryTrandsTable(BaseModel):
    id_trands: int
    category_ru: str
    category_eng: str
    category_id: int
    parent_id: int