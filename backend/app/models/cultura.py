"""
Model da entidade Cultura.

Módulo: Microbiologia (Documento Mestre, seção 6 - Sprint 6). Cada
cultura está vinculada a uma Solicitação e, quando o resultado é
positivo, a um ou mais Microrganismos identificados (relação N:N via
CulturaMicrorganismo, pois uma cultura pode ser polimicrobiana).
"""
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.types import GUID
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

import enum


class ResultadoCulturaEnum(str, enum.Enum):
    EM_ANALISE = "EM_ANALISE"
    POSITIVA = "POSITIVA"
    NEGATIVA = "NEGATIVA"
    CONTAMINADA = "CONTAMINADA"


class Cultura(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "culturas"

    solicitacao_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("solicitacoes.id"), nullable=False, index=True
    )
    resultado: Mapped[ResultadoCulturaEnum] = mapped_column(
        Enum(ResultadoCulturaEnum, name="resultado_cultura_enum"),
        default=ResultadoCulturaEnum.EM_ANALISE,
    )
    liberado_tecnicamente: Mapped[bool] = mapped_column(default=False)
    data_liberacao: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    previsao_liberacao: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    solicitacao = relationship("Solicitacao", lazy="joined")
    microrganismos = relationship(
        "CulturaMicrorganismo",
        back_populates="cultura",
        lazy="joined",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Cultura {self.id} - {self.resultado}>"


class CulturaMicrorganismo(Base):
    """
    Associação N:N entre Cultura e Microrganismo (uma cultura positiva
    pode ter mais de um microrganismo isolado - infecção polimicrobiana).
    """

    __tablename__ = "cultura_microrganismos"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    cultura_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("culturas.id"), nullable=False, index=True
    )
    microrganismo_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("microrganismos.id"), nullable=False, index=True
    )

    microrganismo = relationship("Microrganismo", lazy="joined")
    cultura = relationship("Cultura", back_populates="microrganismos", lazy="joined")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CulturaMicrorganismo cultura={self.cultura_id} micro={self.microrganismo_id}>"
