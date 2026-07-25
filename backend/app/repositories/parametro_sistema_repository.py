"""
Repository de Parâmetros do Sistema.

Não estende BaseRepository porque ParametroSistema não usa soft delete
(parâmetros não são "removidos", apenas atualizados).
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.parametro_sistema import ParametroSistema


class ParametroSistemaRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[ParametroSistema]:
        stmt = select(ParametroSistema).order_by(ParametroSistema.chave)
        return list(self.db.scalars(stmt).all())

    def get_by_chave(self, chave: str) -> ParametroSistema | None:
        stmt = select(ParametroSistema).where(ParametroSistema.chave == chave)
        return self.db.scalars(stmt).first()

    def get_valor_int(self, chave: str, valor_padrao: int) -> int:
        """Lê um parâmetro numérico com fallback seguro caso não exista/seja inválido."""
        parametro = self.get_by_chave(chave)
        if not parametro:
            return valor_padrao
        try:
            return int(parametro.valor)
        except (TypeError, ValueError):
            return valor_padrao

    def atualizar_valor(self, chave: str, novo_valor: str) -> ParametroSistema | None:
        parametro = self.get_by_chave(chave)
        if not parametro:
            return None
        parametro.valor = novo_valor
        self.db.commit()
        self.db.refresh(parametro)
        return parametro
