from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.product import Product
from app.db.models.brand import Brand
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])

@router.post("", response_model=ProductOut)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    if data.brand_id is not None and not db.get(Brand, data.brand_id):
        raise HTTPException(status_code=404, detail="Marca no encontrada.")
    product = Product(
        nombre=data.nombre,
        brand_id=data.brand_id,
        precio_compra_clp=data.precio_compra_clp,
        cantidad=data.cantidad,
        activo=data.activo,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("", response_model=list[ProductOut])
def list_products(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Buscar por nombre"),
    brand_id: Optional[int] = Query(None),
    only_active: Optional[bool] = Query(None),
):
    stmt = select(Product)
    if search:
        stmt = stmt.where(Product.nombre.ilike(f"%{search}%"))
    if brand_id is not None:
        stmt = stmt.where(Product.brand_id == brand_id)
    if only_active is True:
        stmt = stmt.where(Product.activo.is_(True))
    elif only_active is False:
        stmt = stmt.where(Product.activo.is_(False))
    stmt = stmt.order_by(Product.nombre.asc())
    return db.scalars(stmt).all()

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    return product

@router.patch("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")

    payload = data.model_dump(exclude_unset=True)

    if "brand_id" in payload and payload["brand_id"] is not None:
        if not db.get(Brand, payload["brand_id"]):
            raise HTTPException(status_code=404, detail="Marca no encontrada.")

    for field, value in payload.items():
        setattr(product, field, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    db.delete(product)
    db.commit()
    return None
