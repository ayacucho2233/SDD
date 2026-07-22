import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories.reserva_repository import ReservaRepository
from app.repositories.vehiculo_repository import VehiculoRepository
from app.schemas.vehiculo import DisponibilidadOut, VehiculoOut
from app.services.disponibilidad_service import DisponibilidadService

router = APIRouter(tags=["vehiculos"])


@router.get("/vehiculos", response_model=list[VehiculoOut])
async def listar_vehiculos(
    disponible_desde: datetime | None = Query(default=None),
    disponible_hasta: datetime | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[VehiculoOut]:
    if (disponible_desde is None) != (disponible_hasta is None):
        raise HTTPException(
            status_code=400,
            detail="disponible_desde y disponible_hasta deben pasarse juntos",
        )
    if disponible_desde is not None and disponible_hasta <= disponible_desde:  # type: ignore[operator]
        raise HTTPException(status_code=400, detail="disponible_hasta debe ser posterior a disponible_desde")

    vehiculo_repo = VehiculoRepository(session)
    vehiculos = await vehiculo_repo.list()

    resultado: list[VehiculoOut] = []
    for vehiculo in vehiculos:
        disponible = None
        if disponible_desde is not None:
            disponibilidad_service = DisponibilidadService(ReservaRepository(session))
            disponible = vehiculo.estado == "activo" and await disponibilidad_service.esta_disponible(
                vehiculo.id, disponible_desde, disponible_hasta, datetime.now(timezone.utc)
            )
        vehiculo_out = VehiculoOut.model_validate(vehiculo)
        resultado.append(vehiculo_out.model_copy(update={"disponible": disponible}))

    return resultado


@router.get("/vehiculos/{vehiculo_id}/disponibilidad", response_model=DisponibilidadOut)
async def consultar_disponibilidad(
    vehiculo_id: uuid.UUID,
    inicio: datetime,
    fin: datetime,
    session: AsyncSession = Depends(get_session),
) -> DisponibilidadOut:
    if fin <= inicio:
        raise HTTPException(status_code=400, detail="fin debe ser posterior a inicio")

    vehiculo_repo = VehiculoRepository(session)
    vehiculo = await vehiculo_repo.get_by_id(vehiculo_id)
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="El vehículo indicado no existe")

    disponibilidad_service = DisponibilidadService(ReservaRepository(session))
    disponible = vehiculo.estado == "activo" and await disponibilidad_service.esta_disponible(
        vehiculo_id, inicio, fin, datetime.now(timezone.utc)
    )
    return DisponibilidadOut(disponible=disponible)
