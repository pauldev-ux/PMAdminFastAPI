from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

# Para reflejar el estado real del producto (stock puede ser 0)
class ProductBase(BaseModel):
    nombre: str
    brand_id: Optional[int] = None
    precio_compra: Decimal = Field(ge=0)
    precio_venta: Decimal = Field(ge=0)
    cantidad: int = Field(ge=0)            # 👈 puede ser 0 en lecturas
    activo: bool = True
    image_url: Optional[str] = None

# En la creación sí exigimos ingresar stock inicial > 0 y el lote
class ProductCreate(ProductBase):
    cantidad: int = Field(ge=1)            # 👈 crear requiere ≥ 1
    lot_id: int                             # 👈 lote existente obligatorio

# En updates permitir llevar a 0 (o subir)
class ProductUpdate(BaseModel):
    nombre: Optional[str] = None
    brand_id: Optional[int] = None
    precio_compra: Optional[Decimal] = Field(default=None, ge=0)
    precio_venta: Optional[Decimal] = Field(default=None, ge=0)
    cantidad: Optional[int] = Field(default=None, ge=0)  # 👈 permitir 0
    activo: Optional[bool] = None
    image_url: Optional[str] = None

# Respuesta: created_at/updated_at opcionales por si hay nulos antiguos
class ProductOut(ProductBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
