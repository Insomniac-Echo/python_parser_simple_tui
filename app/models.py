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