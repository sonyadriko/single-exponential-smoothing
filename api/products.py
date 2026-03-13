from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

import models
from database import get_db
from schemas.products import ProductCreate, ProductOut
from repositories.product_repository import ProductRepository
from api.auth import get_current_user, get_admin_user

router = APIRouter()


@router.get("", response_model=List[ProductOut])
async def get_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all products."""
    product_repo = ProductRepository(db)
    return product_repo.get_all()


@router.post("")
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user)
):
    """Create a new product (admin only)."""
    product_repo = ProductRepository(db)

    if product_repo.get_by_name(product.name):
        raise HTTPException(status_code=400, detail="Product already exists")

    product_repo.create_product(name=product.name, created_at=datetime.utcnow())
    return {"status": "ok", "msg": "Product created"}


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user)
):
    """Delete a product by ID (admin only)."""
    product_repo = ProductRepository(db)
    product = product_repo.get_by_id(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    sales_count = product_repo.get_sales_count(product.name)
    if sales_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete product with {sales_count} sales records"
        )

    product_repo.delete(product_id)
    return {"status": "ok", "msg": "Product deleted"}
