"""
Schemas de validação de entrada/saída do catálogo de Materiais.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MaterialCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    descricao: str | None = Field(default=None, max_length=300)


class MaterialUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=100)
    descricao: str | None = Field(default=None, max_length=300)


class MaterialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    descricao: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MaterialListOut(BaseModel):
    total: int
    items: list[MaterialOut]
