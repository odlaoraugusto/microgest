"""
Schemas de validação de entrada/saída do módulo Solicitações.
"""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.solicitacao import PrioridadeEnum, StatusSolicitacaoEnum
from app.schemas.paciente import PacienteOut


class SolicitacaoBase(BaseModel):
    paciente_id: uuid.UUID
    material: str = Field(..., min_length=2, max_length=100)
    origem: str | None = Field(default=None, max_length=100)
    prioridade: PrioridadeEnum = PrioridadeEnum.ROTINA
    status: StatusSolicitacaoEnum = StatusSolicitacaoEnum.AGUARDANDO_COLETA
    data_solicitacao: date | None = None
    data_coleta: datetime | None = None
    observacoes: str | None = Field(default=None, max_length=1000)


class SolicitacaoCreate(SolicitacaoBase):
    pass


class SolicitacaoUpdate(BaseModel):
    """Todos os campos opcionais - permite atualização parcial (PATCH)."""

    material: str | None = Field(default=None, min_length=2, max_length=100)
    origem: str | None = Field(default=None, max_length=100)
    prioridade: PrioridadeEnum | None = None
    status: StatusSolicitacaoEnum | None = None
    data_coleta: datetime | None = None
    observacoes: str | None = Field(default=None, max_length=1000)


class SolicitacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    paciente_id: uuid.UUID
    paciente: PacienteOut | None = None
    material: str
    origem: str | None
    prioridade: PrioridadeEnum
    status: StatusSolicitacaoEnum
    data_solicitacao: date
    data_coleta: datetime | None
    observacoes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SolicitacaoListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[SolicitacaoOut]
