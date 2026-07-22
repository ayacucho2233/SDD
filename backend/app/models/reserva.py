import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Reserva(Base):
    __tablename__ = "reservas"
    __table_args__ = (
        CheckConstraint("fecha_fin > fecha_inicio", name="ck_reserva_periodo_valido"),
        Index("ix_reserva_vehiculo_periodo", "vehiculo_id", "fecha_inicio", "fecha_fin"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehiculos.id"), nullable=False
    )
    nombre_empleado: Mapped[str] = mapped_column(String(200), nullable=False)
    legajo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    licencia: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    destino: Mapped[str] = mapped_column(String(300), nullable=False)
    cancelada: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    vehiculo: Mapped["Vehiculo"] = relationship(back_populates="reservas")  # noqa: F821
