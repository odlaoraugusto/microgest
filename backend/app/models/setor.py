"""
Model do catálogo de Setores hospitalares.

Módulo: Configurações (Documento Mestre, seção 6 - Sprint 11). Usado para
padronizar o campo "origem" das Solicitações (ex.: UTI, Enfermaria,
Ambulatório) - importante para os indicadores de distribuição por setor
da CCIH não ficarem fragmentados por variações de digitação ("UTI",
"uti", "U.T.I.").
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Setor(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "setores"

    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    descricao: Mapped[str | None] = mapped_column(String(300), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Setor {self.nome}>"
