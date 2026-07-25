"""
Model do módulo Antibiogramas.

Módulo: Antibiogramas (Documento Mestre, seção 6 - Sprint 7). Um
antibiograma é feito para um isolado específico (CulturaMicrorganismo)
de uma cultura positiva, e contém um resultado S/I/R para cada
antimicrobiano testado.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.types import GUID
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

import enum


class ResultadoSIREnum(str, enum.Enum):
    SENSIVEL = "SENSIVEL"
    INTERMEDIARIO = "INTERMEDIARIO"
    RESISTENTE = "RESISTENTE"


class Antibiograma(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "antibiogramas"

    cultura_microrganismo_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("cultura_microrganismos.id"), nullable=False, index=True
    )
    data_liberacao: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    observacoes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    cultura_microrganismo = relationship("CulturaMicrorganismo", lazy="joined")
    resultados = relationship(
        "AntibiogramaResultado",
        lazy="joined",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Antibiograma {self.id}>"


class AntibiogramaResultado(Base):
    """Resultado S/I/R de um antimicrobiano específico dentro de um antibiograma."""

    __tablename__ = "antibiograma_resultados"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    antibiograma_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("antibiogramas.id"), nullable=False, index=True
    )
    antimicrobiano_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("antimicrobianos.id"), nullable=False, index=True
    )
    resultado: Mapped[ResultadoSIREnum] = mapped_column(
        Enum(ResultadoSIREnum, name="resultado_sir_enum"), nullable=False
    )

    antimicrobiano = relationship("Antimicrobiano", lazy="joined")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AntibiogramaResultado {self.antimicrobiano_id} = {self.resultado}>"
