"""
Model de Parâmetros do Sistema.

Módulo: Configurações (Documento Mestre, seção 6 - Sprint 11). Guarda
configurações simples de chave/valor que hoje seriam constantes no
código (ex.: prazo padrão para considerar uma solicitação vencida),
permitindo que um ADMIN as ajuste sem precisar alterar o código.
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ParametroSistema(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "parametros_sistema"

    chave: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    valor: Mapped[str] = mapped_column(String(500), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ParametroSistema {self.chave}={self.valor}>"
