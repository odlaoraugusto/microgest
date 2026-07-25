"""
Service de Parâmetros do Sistema (Sprint 11).
"""
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories.parametro_sistema_repository import ParametroSistemaRepository


class ParametroSistemaService:
    def __init__(self, db: Session):
        self.repository = ParametroSistemaRepository(db)

    def listar(self):
        return self.repository.listar()

    def atualizar(self, chave: str, novo_valor: str):
        parametro = self.repository.atualizar_valor(chave, novo_valor)
        if not parametro:
            raise NotFoundError(f"Parâmetro '{chave}' não encontrado.")
        return parametro
