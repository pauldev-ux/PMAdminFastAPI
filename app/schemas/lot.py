from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class LotItemCreate(BaseModel):
    product_id: int
    cantidad: int = Field(gt=0)
    costo_unitario_bob: Decimal = Field(ge=0)

class LotCreate(BaseModel):
    nombre: str
    fecha: date
    descripcion: Optional[str] = None
    items: List[LotItemCreate] = Field(default_factory=list)

class LotItemOut(BaseModel):
    id: int
    product_id: int
    cantidad: int
    costo_unitario_bob: Decimal
    subtotal_bob: Decimal
    model_config = ConfigDict(from_attributes=True)

class LotOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    fecha: date
    created_at: datetime
    items: List[LotItemOut]
    # totales de conveniencia
    total_cantidad: int
    total_bob: Decimal
    model_config = ConfigDict(from_attributes=True)
