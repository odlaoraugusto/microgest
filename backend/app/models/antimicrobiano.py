"""
Model do catálogo de Antimicrobianos.

Parte da Base de Conhecimento (Documento Mestre, seção 7). Cadastro
único de cada antimicrobiano, reutilizado em todos os antibiogramas.
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Antimicrobiano(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "antimicrobianos"

    nome: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    sigla: Mapped[str | None] = mapped_column(String(20), nullable=True)
    classe: Mapped[str | None] = mapped_column(String(100), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Antimicrobiano {self.nome}>"
