import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.db.models.product import Product
from app.db.models.brand import Brand
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])

@router.post("", response_model=ProductOut)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    if data.brand_id is not None and not db.get(Brand, data.brand_id):
        raise HTTPException(status_code=404, detail="Marca no encontrada.")
    product = Product(**data.model_dump())
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

# ---------- Upload de imagen ----------
@router.post("/{product_id}/image", response_model=ProductOut)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen.")

    # construir ruta destino
    base = Path(settings.STATIC_DIR)
    uploads = base / settings.UPLOADS_SUBDIR
    uploads.mkdir(parents=True, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1].lower() or ".jpg"
    safe_ext = ext if ext in {".jpg", ".jpeg", ".png", ".webp"} else ".jpg"
    filename = f"product_{product_id}_{int(datetime.utcnow().timestamp())}{safe_ext}"
    full_path = uploads / filename

    # guardar archivo
    data = await file.read()
    if len(data) > 5_000_000:  # 5 MB
        raise HTTPException(status_code=400, detail="Imagen demasiado grande (máx 5MB).")
    with open(full_path, "wb") as f:
        f.write(data)

    # setear URL relativa servida por /static
    product.image_url = f"{settings.MEDIA_URL}/{filename}"
    db.add(product)
    db.commit()
    db.refresh(product)
    return product