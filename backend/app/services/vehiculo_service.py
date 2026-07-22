import uuid
from datetime import datetime, timezone

from app.models.vehiculo import Vehiculo
from app.repositories.reserva_repository import ReservaRepository
from app.repositories.vehiculo_repository import VehiculoRepository
from app.services.exceptions import ConflictoError, RecursoNoEncontradoError


def validar_baja(estado_actual: str, tiene_reservas_activas: bool) -> None:
    """FR-012/FR-015: bloquea la transición a baja_temporal/baja_definitiva
    si el vehículo tiene reservas activas."""
    if tiene_reservas_activas:
        raise ConflictoError("El vehículo tiene reservas vigentes")


def validar_reactivacion(estado_actual: str) -> None:
    """FR-016/FR-019: solo se puede reactivar desde baja_temporal."""
    if estado_actual == "baja_definitiva":
        raise ConflictoError("Un vehículo en baja definitiva no puede reactivarse")
    if estado_actual == "activo":
        raise ConflictoError("El vehículo ya está activo")


class VehiculoService:
    def __init__(self, vehiculo_repository: VehiculoRepository, reserva_repository: ReservaRepository):
        self._vehiculo_repository = vehiculo_repository
        self._reserva_repository = reserva_repository

    async def _get_o_404(self, vehiculo_id: uuid.UUID) -> Vehiculo:
        vehiculo = await self._vehiculo_repository.get_by_id(vehiculo_id)
        if vehiculo is None:
            raise RecursoNoEncontradoError("El vehículo indicado no existe")
        return vehiculo

    async def alta(self, patente: str, tipo: str) -> Vehiculo:
        if await self._vehiculo_repository.get_by_patente(patente) is not None:
            raise ConflictoError("La patente ya existe")  # FR-020
        return await self._vehiculo_repository.create(patente, tipo)

    async def modificar(self, vehiculo_id: uuid.UUID, patente: str, tipo: str) -> Vehiculo:
        vehiculo = await self._get_o_404(vehiculo_id)
        duplicado = await self._vehiculo_repository.get_by_patente(patente, excluir_id=vehiculo_id)
        if duplicado is not None:
            raise ConflictoError("La patente ya existe")  # FR-020
        return await self._vehiculo_repository.update(vehiculo, patente, tipo)

    async def _get_bloqueado_o_404(self, vehiculo_id: uuid.UUID) -> Vehiculo:
        # Bloquea la fila del vehículo antes de chequear reservas activas, para
        # que no pueda colarse una reserva nueva (que también bloquea esta
        # misma fila, ver reserva_service.crear_reserva) entre el chequeo y el
        # cambio de estado.
        vehiculo = await self._vehiculo_repository.get_by_id_for_update(vehiculo_id)
        if vehiculo is None:
            raise RecursoNoEncontradoError("El vehículo indicado no existe")
        return vehiculo

    async def dar_de_baja_temporal(self, vehiculo_id: uuid.UUID) -> Vehiculo:
        vehiculo = await self._get_bloqueado_o_404(vehiculo_id)
        tiene_activas = await self._reserva_repository.tiene_activas(
            vehiculo_id, datetime.now(timezone.utc)
        )
        validar_baja(vehiculo.estado, tiene_activas)  # FR-015
        return await self._vehiculo_repository.set_estado(vehiculo, "baja_temporal")

    async def dar_de_baja_definitiva(self, vehiculo_id: uuid.UUID) -> Vehiculo:
        vehiculo = await self._get_bloqueado_o_404(vehiculo_id)
        tiene_activas = await self._reserva_repository.tiene_activas(
            vehiculo_id, datetime.now(timezone.utc)
        )
        validar_baja(vehiculo.estado, tiene_activas)  # FR-015
        return await self._vehiculo_repository.set_estado(vehiculo, "baja_definitiva")

    async def reactivar(self, vehiculo_id: uuid.UUID) -> Vehiculo:
        vehiculo = await self._get_o_404(vehiculo_id)
        validar_reactivacion(vehiculo.estado)  # FR-019
        return await self._vehiculo_repository.set_estado(vehiculo, "activo")
