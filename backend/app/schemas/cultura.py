"""
Schemas de validação de entrada/saída do módulo Culturas.
"""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.cultura import GrupoCulturaEnum, ResultadoCulturaEnum
from app.schemas.microrganismo import MicrorganismoOut
from app.schemas.solicitacao import SolicitacaoOut


class CulturaCreate(BaseModel):
    solicitacao_id: uuid.UUID
    grupo: GrupoCulturaEnum = GrupoCulturaEnum.CULTURA_GERAL
    resultado: ResultadoCulturaEnum = ResultadoCulturaEnum.EM_ANALISE
    observacoes: str | None = Field(default=None, max_length=1000)
    microrganismo_ids: list[uuid.UUID] = Field(default_factory=list)
    previsao_liberacao: date | None = Field(
        default=None,
        description="Se não informado, é calculada automaticamente a partir do "
        "parâmetro 'prazo_solicitacao_dias'.",
    )


class CulturaUpdate(BaseModel):
    grupo: GrupoCulturaEnum | None = None
    resultado: ResultadoCulturaEnum | None = None
    observacoes: str | None = Field(default=None, max_length=1000)
    microrganismo_ids: list[uuid.UUID] | None = None
    previsao_liberacao: date | None = None


class CulturaMicrorganismoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    microrganismo: MicrorganismoOut


class CulturaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    solicitacao_id: uuid.UUID
    solicitacao: SolicitacaoOut | None = None
    grupo: GrupoCulturaEnum
    resultado: ResultadoCulturaEnum
    liberado_tecnicamente: bool
    data_liberacao: datetime | None
    previsao_liberacao: date | None
    observacoes: str | None
    microrganismos: list[CulturaMicrorganismoOut] = []
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CulturaParcialOut(CulturaOut):
    pendencia: str


class CulturaListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[CulturaOut]


class CulturaParcialListOut(BaseModel):
    total: int
    items: list[CulturaParcialOut]
