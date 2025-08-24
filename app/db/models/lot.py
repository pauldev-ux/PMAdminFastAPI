from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class Lot(Base):
    __tablename__ = "lots"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255), default=None)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)  # fecha de compra/lote
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())

    items: Mapped[list["LotItem"]] = relationship(back_populates="lot", cascade="all, delete-orphan")


class LotItem(Base):
    """
    Un renglón de lote (producto incluido en el lote)
    """
    __tablename__ = "lot_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    lot_id: Mapped[int] = mapped_column(ForeignKey("lots.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"))
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    costo_unitario_bob: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal_bob: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    lot: Mapped["Lot"] = relationship(back_populates="items")
