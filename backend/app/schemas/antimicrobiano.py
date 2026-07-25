"""
Schemas de validação de entrada/saída do catálogo de Antimicrobianos.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AntimicrobianoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150)
    sigla: str | None = Field(default=None, max_length=20)
    classe: str | None = Field(default=None, max_length=100)


class AntimicrobianoCreate(AntimicrobianoBase):
    pass


class AntimicrobianoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=150)
    sigla: str | None = Field(default=None, max_length=20)
    classe: str | None = Field(default=None, max_length=100)


class AntimicrobianoOut(AntimicrobianoBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AntimicrobianoListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AntimicrobianoOut]
