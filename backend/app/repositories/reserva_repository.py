import uuid
from datetime import datetime

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reserva import Reserva


class ReservaRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_activas_por_vehiculo(
        self, vehiculo_id: uuid.UUID, ahora: datetime
    ) -> list[Reserva]:
        """Lectura simple (sin lock) de las reservas activas del vehículo,
        para consultas de disponibilidad de solo lectura (FR-007, FR-010)."""
        stmt = select(Reserva).where(
            Reserva.vehiculo_id == vehiculo_id,
            Reserva.cancelada.is_(False),
            Reserva.fecha_fin >= ahora,
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def tiene_activas(self, vehiculo_id: uuid.UUID, ahora: datetime) -> bool:
        """FR-015: bloquea baja temporal/definitiva si el vehículo tiene
        reservas activas."""
        stmt = select(
            exists().where(
                Reserva.vehiculo_id == vehiculo_id,
                Reserva.cancelada.is_(False),
                Reserva.fecha_fin >= ahora,
            )
        )
        result = await self._session.execute(stmt)
        return bool(result.scalar())

    async def list(self) -> list[Reserva]:
        result = await self._session.execute(select(Reserva).order_by(Reserva.fecha_inicio))
        return list(result.scalars().all())

    async def get_by_id(self, reserva_id: uuid.UUID) -> Reserva | None:
        return await self._session.get(Reserva, reserva_id)

    async def create(self, **kwargs) -> Reserva:
        reserva = Reserva(id=uuid.uuid4(), cancelada=False, **kwargs)
        self._session.add(reserva)
        await self._session.commit()
        await self._session.refresh(reserva)
        return reserva

    async def cancelar(self, reserva: Reserva) -> Reserva:
        reserva.cancelada = True
        await self._session.commit()
        await self._session.refresh(reserva)
        return reserva
