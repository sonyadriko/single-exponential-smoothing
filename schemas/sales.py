from pydantic import BaseModel


class SaleCreate(BaseModel):
    date: str
    product_name: str
    qty: int


class SaleOut(SaleCreate):
    id: int

    class Config:
        from_attributes = True
