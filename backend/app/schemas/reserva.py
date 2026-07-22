import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReservaCreate(BaseModel):
    nombre_empleado: str = Field(min_length=1)
    legajo: str = Field(min_length=1)
    licencia: str = Field(min_length=1)
    vehiculo_id: uuid.UUID
    fecha_inicio: datetime
    fecha_fin: datetime
    destino: str = Field(min_length=1)


class ReservaCancelar(BaseModel):
    legajo: str = Field(min_length=1)


class ReservaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vehiculo_id: uuid.UUID
    nombre_empleado: str
    legajo: str
    licencia: str
    fecha_inicio: datetime
    fecha_fin: datetime
    destino: str
    cancelada: bool
    estado: str
