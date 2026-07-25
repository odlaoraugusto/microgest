"""
Schemas de validação de entrada/saída de Parâmetros do Sistema.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ParametroSistemaUpdate(BaseModel):
    valor: str = Field(..., min_length=1, max_length=500)


class ParametroSistemaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chave: str
    valor: str
    descricao: str | None
    created_at: datetime
    updated_at: datetime
