from typing import List
from sqlalchemy.orm import Session
import models
from repositories.base import BaseRepository


class SaleRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(models.Sale, db)

    def get_all_ordered(self) -> List[models.Sale]:
        return self.db.query(models.Sale).order_by(models.Sale.date).all()

    def get_by_product(self, product_name: str) -> List[models.Sale]:
        return self.db.query(models.Sale).filter(
            models.Sale.product_name == product_name
        ).order_by(models.Sale.date).all()

    def create_sale(self, date: str, product_name: str, qty: int) -> models.Sale:
        sale = models.Sale(date=date, product_name=product_name, qty=qty)
        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)
        return sale

    def delete_all(self) -> int:
        count = self.db.query(models.Sale).delete()
        self.db.commit()
        return count

    def get_recent(self, limit: int = 10) -> List[models.Sale]:
        return self.db.query(models.Sale).order_by(models.Sale.date.desc()).limit(limit).all()

    def get_filtered(self, product_name: str = None, date_from: str = None, date_to: str = None) -> List[models.Sale]:
        """Get sales with optional filters by product name and date range."""
        query = self.db.query(models.Sale)

        if product_name:
            query = query.filter(models.Sale.product_name.ilike(f"%{product_name}%"))

        if date_from:
            query = query.filter(models.Sale.date >= date_from)

        if date_to:
            query = query.filter(models.Sale.date <= date_to)

        return query.order_by(models.Sale.date.desc()).all()
