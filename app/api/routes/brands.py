from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db
from app.db.models.brand import Brand
from app.schemas.brand import BrandCreate, BrandUpdate, BrandOut

router = APIRouter(prefix="/brands", tags=["brands"])

@router.post("", response_model=BrandOut)
def create_brand(data: BrandCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(Brand).where(Brand.nombre == data.nombre))
    if exists:
        raise HTTPException(status_code=400, detail="La marca ya existe.")
    brand = Brand(nombre=data.nombre)
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand

@router.get("", response_model=list[BrandOut])
def list_brands(db: Session = Depends(get_db)):
    return db.scalars(select(Brand).order_by(Brand.nombre)).all()

@router.get("/{brand_id}", response_model=BrandOut)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada.")
    return brand

@router.patch("/{brand_id}", response_model=BrandOut)
def update_brand(brand_id: int, data: BrandUpdate, db: Session = Depends(get_db)):
    brand = db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada.")

    # validar duplicado
    dup = db.scalar(select(Brand).where(Brand.nombre == data.nombre))
    if dup and dup.id != brand_id:
        raise HTTPException(status_code=400, detail="Ya existe otra marca con ese nombre.")

    brand.nombre = data.nombre
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand

@router.delete("/{brand_id}", status_code=204)
def delete_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada.")
    db.delete(brand)
    db.commit()
    return None
