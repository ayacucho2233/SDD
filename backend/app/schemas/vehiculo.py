import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.vehiculo import ESTADOS_VALIDOS, TIPOS_VALIDOS


class VehiculoBase(BaseModel):
    patente: str
    tipo: str

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, value: str) -> str:
        if value not in TIPOS_VALIDOS:
            raise ValueError(f"tipo inválido: debe ser uno de {TIPOS_VALIDOS}")
        return value


class VehiculoCreate(VehiculoBase):
    pass


class VehiculoUpdate(VehiculoBase):
    pass


class VehiculoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patente: str
    tipo: str
    estado: str
    disponible: bool | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value: str) -> str:
        assert value in ESTADOS_VALIDOS
        return value


class DisponibilidadOut(BaseModel):
    disponible: bool
