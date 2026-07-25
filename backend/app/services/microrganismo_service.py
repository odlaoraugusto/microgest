"""
Service do catálogo de Microrganismos (Base de Conhecimento).
"""
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.repositories.microrganismo_repository import MicrorganismoRepository
from app.schemas.microrganismo import MicrorganismoCreate, MicrorganismoUpdate


class MicrorganismoService:
    def __init__(self, db: Session):
        self.repository = MicrorganismoRepository(db)

    def listar(self, termo: str | None, page: int = 1, page_size: int = 20):
        skip = (page - 1) * page_size
        return self.repository.search(termo, skip=skip, limit=page_size)

    def obter(self, microrganismo_id: uuid.UUID):
        microrganismo = self.repository.get_by_id(microrganismo_id)
        if not microrganismo or not microrganismo.is_active:
            raise NotFoundError("Microrganismo não encontrado.")
        return microrganismo

    def criar(self, dados: MicrorganismoCreate):
        existente = self.repository.get_by_nome(dados.nome)
        if existente:
            raise BusinessRuleError(
                "Já existe um microrganismo cadastrado com este nome.",
                errors=[f"nome '{dados.nome}' já está em uso."],
            )
        return self.repository.create(dados.model_dump())

    def atualizar(self, microrganismo_id: uuid.UUID, dados: MicrorganismoUpdate):
        microrganismo = self.obter(microrganismo_id)
        dados_dict = dados.model_dump(exclude_unset=True)
        return self.repository.update(microrganismo, dados_dict)

    def remover(self, microrganismo_id: uuid.UUID):
        microrganismo = self.obter(microrganismo_id)
        self.repository.soft_delete(microrganismo)
