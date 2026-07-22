import uuid
from datetime import datetime, timezone

from app.models.reserva import Reserva
from app.repositories.reserva_repository import ReservaRepository
from app.repositories.vehiculo_repository import VehiculoRepository
from app.services.disponibilidad_service import hay_solapamiento
from app.services.exceptions import (
    ConflictoError,
    NoAutorizadoError,
    RecursoNoEncontradoError,
    SolicitudInvalidaError,
)


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def estado_derivado(reserva: Reserva, ahora: datetime | None = None) -> str:
    """futura / en_curso / pasada, según spec.md § Key Entities."""
    ahora = ahora or _ahora()
    if reserva.fecha_inicio > ahora:
        return "futura"
    if reserva.fecha_inicio <= ahora <= reserva.fecha_fin:
        return "en_curso"
    return "pasada"


def es_activa(reserva: Reserva, ahora: datetime | None = None) -> bool:
    ahora = ahora or _ahora()
    return not reserva.cancelada and reserva.fecha_fin >= ahora


class ReservaService:
    def __init__(
        self,
        reserva_repository: ReservaRepository,
        vehiculo_repository: VehiculoRepository,
    ):
        self._reserva_repository = reserva_repository
        self._vehiculo_repository = vehiculo_repository

    async def crear_reserva(
        self,
        vehiculo_id: uuid.UUID,
        nombre_empleado: str,
        legajo: str,
        licencia: str,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        destino: str,
    ) -> Reserva:
        if fecha_fin <= fecha_inicio:
            raise SolicitudInvalidaError(
                "La fecha/hora de fin debe ser posterior a la de inicio"
            )  # FR-005

        ahora = _ahora()
        if fecha_inicio < ahora:
            raise SolicitudInvalidaError(
                "La fecha/hora de inicio no puede ser anterior al momento actual"
            )  # FR-005a

        # Bloquea la fila del vehículo (SELECT ... FOR UPDATE) ANTES de leer sus
        # reservas activas. Un lock sobre las reservas existentes no alcanza:
        # si el vehículo todavía no tiene ninguna reserva, no hay fila que
        # bloquear y dos transacciones concurrentes verían ambas "disponible".
        # Bloqueando el vehículo (que siempre existe) se serializa cualquier
        # intento concurrente de reservarlo, exista o no una reserva previa
        # (FR-003, SC-003, research.md §3).
        vehiculo = await self._vehiculo_repository.get_by_id_for_update(vehiculo_id)
        if vehiculo is None:
            raise RecursoNoEncontradoError("El vehículo indicado no existe")
        if vehiculo.estado != "activo":
            raise SolicitudInvalidaError("El vehículo no está disponible para reservas")

        activas = await self._reserva_repository.list_activas_por_vehiculo(vehiculo_id, ahora)
        if hay_solapamiento(activas, fecha_inicio, fecha_fin):
            raise ConflictoError(
                "Ya existe una reserva activa para ese vehículo en el período solicitado"
            )  # FR-003

        return await self._reserva_repository.create(
            vehiculo_id=vehiculo_id,
            nombre_empleado=nombre_empleado,
            legajo=legajo,
            licencia=licencia,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            destino=destino,
        )

    async def listar_reservas(self, estado: str | None = None) -> list[Reserva]:
        reservas = await self._reserva_repository.list()
        if estado is None:
            return reservas
        ahora = _ahora()
        return [r for r in reservas if estado_derivado(r, ahora) == estado]

    async def cancelar_reserva(self, reserva_id: uuid.UUID, legajo: str) -> Reserva:
        reserva = await self._reserva_repository.get_by_id(reserva_id)
        if reserva is None:
            raise RecursoNoEncontradoError("La reserva indicada no existe")

        if reserva.legajo != legajo:
            raise NoAutorizadoError(
                "Solo el legajo que creó la reserva puede cancelarla"
            )  # FR-009

        if not es_activa(reserva):
            raise ConflictoError(
                "La reserva no admite cancelación en su estado actual"
            )  # FR-009a

        return await self._reserva_repository.cancelar(reserva)
