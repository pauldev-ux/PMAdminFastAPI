from decimal import Decimal
from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.lot import Lot, LotItem
from app.db.models.product import Product
from app.schemas.lot import LotCreate, LotOut, LotItemCreate

router = APIRouter(prefix="/lots", tags=["lots"])

def _lot_to_out(lot: Lot) -> LotOut:
    total_qty = sum(li.cantidad for li in lot.items)
    total_bob = sum(Decimal(li.subtotal_bob) for li in lot.items)
    return LotOut(
        id=lot.id,
        nombre=lot.nombre,
        descripcion=lot.descripcion,
        fecha=lot.fecha,
        created_at=lot.created_at,
        items=lot.items,
        total_cantidad=total_qty,
        total_bob=total_bob,
    )

@router.post("", response_model=LotOut)
def create_lot(data: LotCreate, db: Session = Depends(get_db)):
    # validar productos
    ids = [it.product_id for it in data.items]
    if ids:
        prods = db.scalars(select(Product).where(Product.id.in_(ids))).all()
        found = {p.id for p in prods}
        missing = [i for i in ids if i not in found]
        if missing:
            raise HTTPException(status_code=404, detail=f"Producto(s) inexistente(s): {missing}")

    lot = Lot(nombre=data.nombre, descripcion=data.descripcion, fecha=data.fecha)
    db.add(lot)
    db.flush()  # id

    for it in data.items:
        costo = Decimal(str(it.costo_unitario_bob))
        sub = (costo * Decimal(it.cantidad)).quantize(Decimal("0.01"))
        db.add(LotItem(
            lot_id=lot.id,
            product_id=it.product_id,
            cantidad=it.cantidad,
            costo_unitario_bob=costo,
            subtotal_bob=sub,
        ))
        # aumentar stock y (opcional) actualizar costo del producto
        prod = db.get(Product, it.product_id)
        prod.cantidad = (prod.cantidad or 0) + it.cantidad
        prod.precio_compra = costo  # o mantener el anterior si prefieres

    db.commit()
    db.refresh(lot)
    # forzar carga items
    lot.items  # noqa
    return _lot_to_out(lot)

@router.post("/{lot_id}/items", response_model=LotOut)
def add_items_to_lot(lot_id: int, items: List[LotItemCreate], db: Session = Depends(get_db)):
    lot = db.get(Lot, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lote no existe")
    if not items:
        return _lot_to_out(lot)

    ids = [it.product_id for it in items]
    prods = db.scalars(select(Product).where(Product.id.in_(ids))).all()
    found = {p.id for p in prods}
    missing = [i for i in ids if i not in found]
    if missing:
        raise HTTPException(status_code=404, detail=f"Producto(s) inexistente(s): {missing}")

    for it in items:
        costo = Decimal(str(it.costo_unitario_bob))
        sub = (costo * Decimal(it.cantidad)).quantize(Decimal("0.01"))
        db.add(LotItem(
            lot_id=lot.id,
            product_id=it.product_id,
            cantidad=it.cantidad,
            costo_unitario_bob=costo,
            subtotal_bob=sub,
        ))
        prod = db.get(Product, it.product_id)
        prod.cantidad = (prod.cantidad or 0) + it.cantidad
        prod.precio_compra = costo

    db.commit()
    db.refresh(lot)
    lot.items
    return _lot_to_out(lot)

@router.get("", response_model=list[LotOut])
def list_lots(
    db: Session = Depends(get_db),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
):
    stmt = select(Lot)
    if from_date is not None:
        stmt = stmt.where(Lot.fecha >= from_date)
    if to_date is not None:
        stmt = stmt.where(Lot.fecha <= to_date)
    stmt = stmt.order_by(Lot.fecha.desc(), Lot.created_at.desc())

    lots = db.scalars(stmt).all()
    # cargar items
    for l in lots:
        _ = l.items
    return [_lot_to_out(l) for l in lots]

@router.get("/{lot_id}", response_model=LotOut)
def get_lot(lot_id: int, db: Session = Depends(get_db)):
    lot = db.get(Lot, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lote no existe")
    lot.items
    return _lot_to_out(lot)
