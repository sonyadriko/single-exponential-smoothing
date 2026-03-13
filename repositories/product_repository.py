from typing import Optional, List
from sqlalchemy.orm import Session
import models
from repositories.base import BaseRepository


class ProductRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(models.Product, db)

    def get_by_name(self, name: str) -> Optional[models.Product]:
        return self.db.query(models.Product).filter(models.Product.name == name).first()

    def create_product(self, name: str, created_at=None) -> models.Product:
        product = models.Product(name=name, created_at=created_at)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_sales_count(self, product_name: str) -> int:
        return self.db.query(models.Sale).filter(models.Sale.product_name == product_name).count()
