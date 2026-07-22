import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

TIPOS_VALIDOS = ("auto", "camioneta")
ESTADOS_VALIDOS = ("activo", "baja_temporal", "baja_definitiva")


class Vehiculo(Base):
    __tablename__ = "vehiculos"
    __table_args__ = (
        CheckConstraint("tipo IN ('auto','camioneta')", name="ck_vehiculo_tipo"),
        CheckConstraint(
            "estado IN ('activo','baja_temporal','baja_definitiva')",
            name="ck_vehiculo_estado",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patente: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="activo")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    reservas: Mapped[list["Reserva"]] = relationship(  # noqa: F821
        back_populates="vehiculo"
    )
