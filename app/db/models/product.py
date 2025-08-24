from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, ForeignKey, Numeric, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), index=True)
    brand_id: Mapped[Optional[int]] = mapped_column(ForeignKey("brands.id", ondelete="SET NULL"), nullable=True)

    # Precios (ambos DECIMAL(12,2))
    precio_compra: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, server_default="0")
    precio_venta: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, server_default="0")
    # Stock actual
    cantidad: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    # Imagen (URL relativa tipo /static/uploads/archivo.jpg)
    image_url: Mapped[Optional[str]] = mapped_column(String(255), default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
