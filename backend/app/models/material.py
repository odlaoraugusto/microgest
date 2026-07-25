"""
Model do catálogo de Materiais biológicos.

Módulo: Configurações (Documento Mestre, seção 6 - Sprint 11). Usado para
padronizar o campo "material" das Solicitações (ex.: Hemocultura, Urina,
Escarro) e evitar variações de digitação que fragmentariam relatórios e
indicadores.
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Material(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "materiais"

    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    descricao: Mapped[str | None] = mapped_column(String(300), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Material {self.nome}>"
