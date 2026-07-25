"""
Schemas de validação de entrada/saída do módulo Antibiogramas.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.antibiograma import ResultadoSIREnum
from app.schemas.antimicrobiano import AntimicrobianoOut
from app.schemas.microrganismo import MicrorganismoOut


class ResultadoAntimicrobianoIn(BaseModel):
    antimicrobiano_id: uuid.UUID
    resultado: ResultadoSIREnum


class AntibiogramaCreate(BaseModel):
    cultura_microrganismo_id: uuid.UUID
    observacoes: str | None = Field(default=None, max_length=1000)
    resultados: list[ResultadoAntimicrobianoIn] = Field(default_factory=list)


class AntibiogramaUpdate(BaseModel):
    observacoes: str | None = Field(default=None, max_length=1000)
    resultados: list[ResultadoAntimicrobianoIn] | None = None


class AntibiogramaResultadoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    antimicrobiano: AntimicrobianoOut
    resultado: ResultadoSIREnum


class CulturaMicrorganismoResumoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    microrganismo: MicrorganismoOut


class AntibiogramaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cultura_microrganismo_id: uuid.UUID
    cultura_microrganismo: CulturaMicrorganismoResumoOut | None = None
    data_liberacao: datetime | None
    observacoes: str | None
    resultados: list[AntibiogramaResultadoOut] = []
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AntibiogramaListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AntibiogramaOut]
