from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProductCreate(BaseModel):
    name: str


class ProductOut(BaseModel):
    id: int
    name: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
