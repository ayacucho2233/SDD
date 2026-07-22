import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehiculo import Vehiculo


class VehiculoRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(self) -> list[Vehiculo]:
        result = await self._session.execute(select(Vehiculo).order_by(Vehiculo.patente))
        return list(result.scalars().all())

    async def get_by_id(self, vehiculo_id: uuid.UUID) -> Vehiculo | None:
        return await self._session.get(Vehiculo, vehiculo_id)

    async def get_by_id_for_update(self, vehiculo_id: uuid.UUID) -> Vehiculo | None:
        """Bloquea la fila del vehículo (SELECT ... FOR UPDATE) — ver research.md §3."""
        result = await self._session.execute(
            select(Vehiculo).where(Vehiculo.id == vehiculo_id).with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_by_patente(
        self, patente: str, excluir_id: uuid.UUID | None = None
    ) -> Vehiculo | None:
        stmt = select(Vehiculo).where(Vehiculo.patente == patente)
        if excluir_id is not None:
            stmt = stmt.where(Vehiculo.id != excluir_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, patente: str, tipo: str) -> Vehiculo:
        vehiculo = Vehiculo(id=uuid.uuid4(), patente=patente, tipo=tipo, estado="activo")
        self._session.add(vehiculo)
        await self._session.commit()
        await self._session.refresh(vehiculo)
        return vehiculo

    async def update(self, vehiculo: Vehiculo, patente: str, tipo: str) -> Vehiculo:
        vehiculo.patente = patente
        vehiculo.tipo = tipo
        await self._session.commit()
        await self._session.refresh(vehiculo)
        return vehiculo

    async def set_estado(self, vehiculo: Vehiculo, estado: str) -> Vehiculo:
        vehiculo.estado = estado
        await self._session.commit()
        await self._session.refresh(vehiculo)
        return vehiculo
