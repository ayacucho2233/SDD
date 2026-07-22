import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories.reserva_repository import ReservaRepository
from app.repositories.vehiculo_repository import VehiculoRepository
from app.schemas.reserva import ReservaCancelar, ReservaCreate, ReservaOut
from app.services.exceptions import (
    ConflictoError,
    NoAutorizadoError,
    RecursoNoEncontradoError,
    SolicitudInvalidaError,
)
from app.services.reserva_service import ReservaService, estado_derivado

router = APIRouter(tags=["reservas"])


def _build_service(session: AsyncSession) -> ReservaService:
    return ReservaService(ReservaRepository(session), VehiculoRepository(session))


def _to_out(reserva) -> ReservaOut:
    return ReservaOut(
        id=reserva.id,
        vehiculo_id=reserva.vehiculo_id,
        nombre_empleado=reserva.nombre_empleado,
        legajo=reserva.legajo,
        licencia=reserva.licencia,
        fecha_inicio=reserva.fecha_inicio,
        fecha_fin=reserva.fecha_fin,
        destino=reserva.destino,
        cancelada=reserva.cancelada,
        estado=estado_derivado(reserva),
    )


@router.post("/reservas", response_model=ReservaOut, status_code=status.HTTP_201_CREATED)
async def crear_reserva(
    payload: ReservaCreate, session: AsyncSession = Depends(get_session)
) -> ReservaOut:
    service = _build_service(session)
    try:
        reserva = await service.crear_reserva(
            vehiculo_id=payload.vehiculo_id,
            nombre_empleado=payload.nombre_empleado,
            legajo=payload.legajo,
            licencia=payload.licencia,
            fecha_inicio=payload.fecha_inicio,
            fecha_fin=payload.fecha_fin,
            destino=payload.destino,
        )
    except SolicitudInvalidaError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RecursoNoEncontradoError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConflictoError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return _to_out(reserva)


@router.get("/reservas", response_model=list[ReservaOut])
async def listar_reservas(
    estado: str | None = Query(default=None, pattern="^(futura|en_curso|pasada)$"),
    session: AsyncSession = Depends(get_session),
) -> list[ReservaOut]:
    service = _build_service(session)
    reservas = await service.listar_reservas(estado)
    return [_to_out(r) for r in reservas]


@router.post("/reservas/{reserva_id}/cancelar", response_model=ReservaOut)
async def cancelar_reserva(
    reserva_id: uuid.UUID,
    payload: ReservaCancelar,
    session: AsyncSession = Depends(get_session),
) -> ReservaOut:
    service = _build_service(session)
    try:
        reserva = await service.cancelar_reserva(reserva_id, payload.legajo)
    except RecursoNoEncontradoError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except NoAutorizadoError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ConflictoError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return _to_out(reserva)
