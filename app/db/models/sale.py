from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha_venta: Mapped[date] = mapped_column(Date)
    nota: Mapped[str | None] = mapped_column(String(250), default=None)

    total_bob: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, server_default="0")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())

    items: Mapped[list["SaleItem"]] = relationship(
        back_populates="sale",
        cascade="all, delete-orphan"
    )

class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)

    cantidad: Mapped[int] = mapped_column(Integer)
    precio_unitario_bob: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    subtotal_bob: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    sale: Mapped["Sale"] = relationship(back_populates="items")
