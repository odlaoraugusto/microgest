"""
Schemas de validação de entrada/saída do catálogo de Microrganismos.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.microrganismo import GramEnum, TipoMicrorganismoEnum


class MicrorganismoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150)
    nome_cientifico: str | None = Field(default=None, max_length=150)
    gram: GramEnum = GramEnum.NAO_SE_APLICA
    tipo: TipoMicrorganismoEnum = TipoMicrorganismoEnum.BACTERIA
    familia: str | None = Field(default=None, max_length=100)
    relevancia_clinica: str | None = Field(default=None, max_length=500)


class MicrorganismoCreate(MicrorganismoBase):
    pass


class MicrorganismoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=150)
    nome_cientifico: str | None = Field(default=None, max_length=150)
    gram: GramEnum | None = None
    tipo: TipoMicrorganismoEnum | None = None
    familia: str | None = Field(default=None, max_length=100)
    relevancia_clinica: str | None = Field(default=None, max_length=500)


class MicrorganismoOut(MicrorganismoBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MicrorganismoListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[MicrorganismoOut]
