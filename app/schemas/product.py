from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ProductBase(BaseModel):
    nombre: str
    brand_id: Optional[int] = None
    precio_compra: Decimal = Field(ge=0)
    precio_venta: Decimal = Field(ge=0)
    cantidad: int = Field(ge=0)
    activo: bool = True
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    nombre: Optional[str] = None
    brand_id: Optional[int] = None
    precio_compra: Optional[Decimal] = Field(default=None, ge=0)
    precio_venta: Optional[Decimal] = Field(default=None, ge=0)
    cantidad: Optional[int] = Field(default=None, ge=0)
    activo: Optional[bool] = None
    image_url: Optional[str] = None  # por si quieres setear/quitar URL manualmente

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
