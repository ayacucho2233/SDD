import uuid
from datetime import datetime
from typing import Protocol

from app.repositories.reserva_repository import ReservaRepository


class _PeriodoReserva(Protocol):
    fecha_inicio: datetime
    fecha_fin: datetime


def hay_solapamiento(
    reservas_existentes: list[_PeriodoReserva], inicio: datetime, fin: datetime
) -> bool:
    """Dos períodos [a_inicio, a_fin) y [b_inicio, b_fin) se solapan si
    a_inicio < b_fin y b_inicio < a_fin (FR-003)."""
    return any(r.fecha_inicio < fin and inicio < r.fecha_fin for r in reservas_existentes)


class DisponibilidadService:
    def __init__(self, reserva_repository: ReservaRepository):
        self._reserva_repository = reserva_repository

    async def esta_disponible(
        self, vehiculo_id: uuid.UUID, inicio: datetime, fin: datetime, ahora: datetime
    ) -> bool:
        """Consulta de solo lectura (sin lock) — para GET /vehiculos y
        GET /vehiculos/{id}/disponibilidad."""
        activas = await self._reserva_repository.list_activas_por_vehiculo(vehiculo_id, ahora)
        return not hay_solapamiento(activas, inicio, fin)
