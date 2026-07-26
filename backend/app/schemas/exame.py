"""
Schemas do módulo Exames.

O módulo Exames é uma camada aditiva que compõe Solicitação + Cultura
numa única operação, refletindo o fluxo real do laboratório (a coleta
já aconteceu no sistema do hospital antes de qualquer coisa chegar ao
MicroGest). Ele não substitui os módulos Solicitações/Microbiologia,
que continuam existindo intactos para o caso de agendamento antecipado.

Não há um `ExameOut` próprio: a resposta de todos os endpoints reutiliza
`CulturaOut` (ver app.schemas.cultura), já que uma Cultura com sua
Solicitação aninhada É a representação completa de um "exame".
"""
import uuid
from datetime import date

from pydantic import BaseModel, Field

from app.models.cultura import ResultadoCulturaEnum
from app.models.solicitacao import PrioridadeEnum


class ExameCreate(BaseModel):
    # Campos da Solicitação
    paciente_id: uuid.UUID
    material: str = Field(..., min_length=2, max_length=100)
    origem: str | None = Field(default=None, max_length=100)
    prioridade: PrioridadeEnum = PrioridadeEnum.ROTINA
    observacoes_solicitacao: str | None = Field(default=None, max_length=1000)

    # Campos da Cultura
    resultado: ResultadoCulturaEnum = ResultadoCulturaEnum.EM_ANALISE
    microrganismo_ids: list[uuid.UUID] = Field(default_factory=list)
    previsao_liberacao: date | None = Field(
        default=None,
        description="Se não informado, é calculada automaticamente a partir do "
        "parâmetro 'prazo_solicitacao_dias'.",
    )
    observacoes_cultura: str | None = Field(default=None, max_length=1000)


class ExameUpdate(BaseModel):
    """Todos os campos opcionais - permite atualização parcial (PATCH)."""

    # Campos da Solicitação
    material: str | None = Field(default=None, min_length=2, max_length=100)
    origem: str | None = Field(default=None, max_length=100)
    prioridade: PrioridadeEnum | None = None
    observacoes_solicitacao: str | None = Field(default=None, max_length=1000)

    # Campos da Cultura
    resultado: ResultadoCulturaEnum | None = None
    microrganismo_ids: list[uuid.UUID] | None = None
    previsao_liberacao: date | None = None
    observacoes_cultura: str | None = Field(default=None, max_length=1000)
