from collections import defaultdict
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db
from app.db.models.product import Product
from app.db.models.sale import Sale, SaleItem
from app.schemas.sale import SaleCreate, SaleOut
from datetime import date

router = APIRouter(prefix="/sales", tags=["sales"])

@router.post("", response_model=SaleOut)
def create_sale(data: SaleCreate, db: Session = Depends(get_db)):
    if not data.items:
        raise HTTPException(status_code=400, detail="La venta debe tener al menos un ítem.")

    # 1) Validar existencia de productos y stock disponible (bloqueando filas)
    ids = sorted({item.product_id for item in data.items})  # orden estable para evitar deadlocks
    prods = db.execute(
        select(Product).where(Product.id.in_(ids)).with_for_update()
    ).scalars().all()
    prod_map = {p.id: p for p in prods}

    # Verifica productos faltantes
    missing = [pid for pid in ids if pid not in prod_map]
    if missing:
        raise HTTPException(status_code=404, detail=f"Producto(s) no encontrado(s): {missing}")

    # Sumar cantidades por producto (por si el mismo product_id viene repetido)
    req_qty: dict[int, int] = defaultdict(int)
    for it in data.items:
        req_qty[it.product_id] += it.cantidad

    # Chequear stock
    for pid, qty in req_qty.items():
        disp = prod_map[pid].cantidad or 0
        if qty > disp:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para producto {pid}. Disponible: {disp}, requerido: {qty}")

    # 2) Crear venta y descontar stocks
    try:
        sale = Sale(fecha_venta=data.fecha_venta, nota=data.nota, total_bob=Decimal("0.00"))
        db.add(sale)
        db.flush()  # para tener sale.id

        total = Decimal("0.00")
        for it in data.items:
            prod = prod_map[it.product_id]
            # usa precio enviado o el del producto
            precio = it.precio_unitario_bob if it.precio_unitario_bob is not None else prod.precio_venta
            if precio is None:
                raise HTTPException(status_code=400, detail=f"Producto {prod.id} no tiene precio_venta definido.")
            subtotal = (Decimal(str(precio)) * Decimal(it.cantidad)).quantize(Decimal("0.01"))
            si = SaleItem(
                sale_id=sale.id,
                product_id=it.product_id,
                cantidad=it.cantidad,
                precio_unitario_bob=precio,
                subtotal_bob=subtotal,
            )
            db.add(si)
            # descontar stock
            prod.cantidad = (prod.cantidad or 0) - it.cantidad
            total += subtotal

        sale.total_bob = total
        db.commit()

        # Cargar items para respuesta
        db.refresh(sale)
        items = db.execute(select(SaleItem).where(SaleItem.sale_id == sale.id)).scalars().all()
        sale.items = items  # para serializar
        return sale

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creando venta: {e}")

@router.get("", response_model=list[SaleOut])
def list_sales(
    db: Session = Depends(get_db),
    from_date: date | None = Query(default=None, description="YYYY-MM-DD"),
    to_date: date | None = Query(default=None, description="YYYY-MM-DD"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    stmt = (
        select(Sale)
        .options(selectinload(Sale.items))   # evita N+1 queries
        .order_by(Sale.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if from_date:
        stmt = stmt.where(Sale.fecha_venta >= from_date)
    if to_date:
        stmt = stmt.where(Sale.fecha_venta <= to_date)

    return db.scalars(stmt).all()


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.get(Sale, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada.")
    sale.items = db.execute(select(SaleItem).where(SaleItem.sale_id == sale.id)).scalars().all()
    return sale
