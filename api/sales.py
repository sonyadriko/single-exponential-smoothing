from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

import models
from database import get_db
from schemas.sales import SaleCreate, SaleOut
from repositories.sale_repository import SaleRepository
from api.auth import get_current_user_or_session, get_admin_user_or_session

router = APIRouter()


@router.get("", response_model=List[SaleOut])
async def get_sales(
    product_name: Optional[str] = Query(None, description="Filter by product name (partial match)"),
    date_from: Optional[str] = Query(None, description="Filter by date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter by date to (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_or_session)
):
    """Get all sales records with optional filters."""
    sale_repo = SaleRepository(db)

    # Use filtered method if any filter is provided, otherwise get all
    if product_name or date_from or date_to:
        return sale_repo.get_filtered(
            product_name=product_name,
            date_from=date_from,
            date_to=date_to
        )

    return sale_repo.get_all_ordered()


@router.get("/product/{product_name}")
async def get_sales_by_product(
    product_name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_or_session)
):
    """Get all sales for a specific product."""
    sale_repo = SaleRepository(db)
    sales = sale_repo.get_by_product(product_name)
    return [{"id": s.id, "date": s.date, "product_name": s.product_name, "qty": s.qty} for s in sales]


@router.post("")
async def add_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user_or_session)
):
    """Add a new sale record (admin only)."""
    sale_repo = SaleRepository(db)
    sale_repo.create_sale(date=sale.date, product_name=sale.product_name, qty=sale.qty)
    return {"status": "ok", "msg": "Sale added"}


@router.delete("/{sale_id}")
async def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user_or_session)
):
    """Delete a sale record by ID (admin only)."""
    sale_repo = SaleRepository(db)
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    sale_repo.delete(sale_id)
    return {"status": "ok", "msg": "Sale deleted"}
