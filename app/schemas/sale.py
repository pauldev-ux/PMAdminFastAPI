from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class SaleItemIn(BaseModel):
    product_id: int
    cantidad: int = Field(gt=0)
    precio_unitario_bob: Decimal = Field(ge=0)

class SaleCreate(BaseModel):
    fecha_venta: date
    items: List[SaleItemIn]
    nota: Optional[str] = None

class SaleItemOut(BaseModel):
    id: int
    product_id: int
    cantidad: int
    precio_unitario_bob: Decimal
    subtotal_bob: Decimal
    model_config = ConfigDict(from_attributes=True)

class SaleOut(BaseModel):
    id: int
    fecha_venta: date
    nota: Optional[str]
    total_bob: Decimal
    created_at: datetime
    items: List[SaleItemOut]
    model_config = ConfigDict(from_attributes=True)
