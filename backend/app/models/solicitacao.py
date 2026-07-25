"""
Model da entidade Solicitação.

Módulo: Solicitações (Documento Mestre, seção 6 - Sprint 5).
Uma solicitação representa o pedido de exame microbiológico feito para
um paciente: material biológico, origem da coleta, prioridade e status
do fluxo (da solicitação até a liberação do resultado).
"""
from datetime import date, datetime
import uuid

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.types import GUID
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

import enum


class PrioridadeEnum(str, enum.Enum):
    ROTINA = "ROTINA"
    URGENTE = "URGENTE"
    EMERGENCIA = "EMERGENCIA"


class StatusSolicitacaoEnum(str, enum.Enum):
    AGUARDANDO_COLETA = "AGUARDANDO_COLETA"
    COLETADO = "COLETADO"
    EM_ANALISE = "EM_ANALISE"
    LIBERADO = "LIBERADO"
    CANCELADO = "CANCELADO"


class Solicitacao(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "solicitacoes"

    paciente_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("pacientes.id"), nullable=False, index=True
    )
    material: Mapped[str] = mapped_column(String(100), nullable=False)
    origem: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prioridade: Mapped[PrioridadeEnum] = mapped_column(
        Enum(PrioridadeEnum, name="prioridade_enum"), default=PrioridadeEnum.ROTINA
    )
    status: Mapped[StatusSolicitacaoEnum] = mapped_column(
        Enum(StatusSolicitacaoEnum, name="status_solicitacao_enum"),
        default=StatusSolicitacaoEnum.AGUARDANDO_COLETA,
    )
    data_solicitacao: Mapped[date] = mapped_column(
        Date, nullable=False, default=date.today
    )
    data_coleta: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    observacoes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    paciente = relationship("Paciente", lazy="joined")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Solicitacao {self.id} - {self.material} ({self.status})>"
