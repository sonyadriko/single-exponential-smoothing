from pydantic import BaseModel
from datetime import date


class SaleCreate(BaseModel):
    date: date | str  # Accept both date and str for flexibility
    product_name: str
    qty: int


class SaleOut(BaseModel):
    id: int
    date: date
    product_name: str
    qty: int

    class Config:
        from_attributes = True
