from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ProductBase(BaseModel):
    nombre: str
    brand_id: Optional[int] = None
    precio_compra_clp: Decimal = Field(ge=0)
    cantidad: int = Field(ge=0)
    activo: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    nombre: Optional[str] = None
    brand_id: Optional[int] = None
    precio_compra_clp: Optional[Decimal] = Field(default=None, ge=0)
    cantidad: Optional[int] = Field(default=None, ge=0)
    activo: Optional[bool] = None

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
