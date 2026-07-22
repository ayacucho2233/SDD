import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin
from app.database import get_session
from app.repositories.reserva_repository import ReservaRepository
from app.repositories.vehiculo_repository import VehiculoRepository
from app.schemas.vehiculo import VehiculoCreate, VehiculoOut, VehiculoUpdate
from app.services.exceptions import ConflictoError, RecursoNoEncontradoError
from app.services.vehiculo_service import VehiculoService

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def _build_service(session: AsyncSession) -> VehiculoService:
    return VehiculoService(VehiculoRepository(session), ReservaRepository(session))


@router.post(
    "/vehiculos", response_model=VehiculoOut, status_code=status.HTTP_201_CREATED
)
async def alta_vehiculo(
    payload: VehiculoCreate, session: AsyncSession = Depends(get_session)
) -> VehiculoOut:
    service = _build_service(session)
    try:
        vehiculo = await service.alta(payload.patente, payload.tipo)
    except ConflictoError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return VehiculoOut.model_validate(vehiculo)


@router.put("/vehiculos/{vehiculo_id}", response_model=VehiculoOut)
async def modificar_vehiculo(
    vehiculo_id: uuid.UUID, payload: VehiculoUpdate, session: AsyncSession = Depends(get_session)
) -> VehiculoOut:
    service = _build_service(session)
    try:
        vehiculo = await service.modificar(vehiculo_id, payload.patente, payload.tipo)
    except RecursoNoEncontradoError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConflictoError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return VehiculoOut.model_validate(vehiculo)


@router.post("/vehiculos/{vehiculo_id}/baja-temporal", response_model=VehiculoOut)
async def baja_temporal(
    vehiculo_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> VehiculoOut:
    service = _build_service(session)
    try:
        vehiculo = await service.dar_de_baja_temporal(vehiculo_id)
    except RecursoNoEncontradoError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConflictoError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return VehiculoOut.model_validate(vehiculo)


@router.post("/vehiculos/{vehiculo_id}/baja-definitiva", response_model=VehiculoOut)
async def baja_definitiva(
    vehiculo_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> VehiculoOut:
    service = _build_service(session)
    try:
        vehiculo = await service.dar_de_baja_definitiva(vehiculo_id)
    except RecursoNoEncontradoError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConflictoError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return VehiculoOut.model_validate(vehiculo)


@router.post("/vehiculos/{vehiculo_id}/reactivar", response_model=VehiculoOut)
async def reactivar_vehiculo(
    vehiculo_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> VehiculoOut:
    service = _build_service(session)
    try:
        vehiculo = await service.reactivar(vehiculo_id)
    except RecursoNoEncontradoError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConflictoError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return VehiculoOut.model_validate(vehiculo)
