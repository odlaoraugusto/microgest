"""
Service do módulo Antibiogramas.

Regras de negócio:
- Só é possível criar um antibiograma para um isolado (CulturaMicrorganismo)
  que pertence a uma cultura com resultado POSITIVA.
- Cada antimicrobiano referenciado nos resultados precisa existir.
- Não é permitido repetir o mesmo antimicrobiano duas vezes no mesmo
  antibiograma.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.cultura import ResultadoCulturaEnum
from app.repositories.antibiograma_repository import AntibiogramaRepository
from app.repositories.antimicrobiano_repository import AntimicrobianoRepository
from app.repositories.cultura_microrganismo_repository import (
    CulturaMicrorganismoRepository,
)
from app.schemas.antibiograma import AntibiogramaCreate, AntibiogramaUpdate


class AntibiogramaService:
    def __init__(self, db: Session):
        self.repository = AntibiogramaRepository(db)
        self.cultura_microrganismo_repository = CulturaMicrorganismoRepository(db)
        self.antimicrobiano_repository = AntimicrobianoRepository(db)

    def listar(
        self,
        cultura_microrganismo_id: uuid.UUID | None,
        page: int = 1,
        page_size: int = 20,
    ):
        skip = (page - 1) * page_size
        return self.repository.search(
            cultura_microrganismo_id=cultura_microrganismo_id, skip=skip, limit=page_size
        )

    def obter(self, antibiograma_id: uuid.UUID):
        antibiograma = self.repository.get_by_id(antibiograma_id)
        if not antibiograma or not antibiograma.is_active:
            raise NotFoundError("Antibiograma não encontrado.")
        return antibiograma

    def _validar_resultados(self, resultados: list) -> None:
        ids = [r.antimicrobiano_id for r in resultados]
        if len(ids) != len(set(ids)):
            raise BusinessRuleError(
                "Não é possível repetir o mesmo antimicrobiano no antibiograma.",
            )
        for r in resultados:
            antimicrobiano = self.antimicrobiano_repository.get_by_id(r.antimicrobiano_id)
            if not antimicrobiano or not antimicrobiano.is_active:
                raise BusinessRuleError(
                    "Um dos antimicrobianos informados não existe ou está inativo.",
                    errors=[f"antimicrobiano_id '{r.antimicrobiano_id}' inválido."],
                )

    def criar(self, dados: AntibiogramaCreate):
        isolado = self.cultura_microrganismo_repository.get_by_id(
            dados.cultura_microrganismo_id
        )
        if not isolado:
            raise BusinessRuleError(
                "Isolado (cultura/microrganismo) informado não existe.",
                errors=[f"cultura_microrganismo_id '{dados.cultura_microrganismo_id}' inválido."],
            )
        if isolado.cultura.resultado != ResultadoCulturaEnum.POSITIVA:
            raise BusinessRuleError(
                "Só é possível criar antibiograma para um isolado de cultura POSITIVA.",
            )

        self._validar_resultados(dados.resultados)

        antibiograma = self.repository.create(
            {
                "cultura_microrganismo_id": dados.cultura_microrganismo_id,
                "observacoes": dados.observacoes,
            }
        )

        if dados.resultados:
            self.repository.definir_resultados(
                antibiograma.id,
                [r.model_dump() for r in dados.resultados],
            )

        return self.repository.get_by_id(antibiograma.id)

    def atualizar(self, antibiograma_id: uuid.UUID, dados: AntibiogramaUpdate):
        antibiograma = self.obter(antibiograma_id)

        if dados.resultados is not None:
            self._validar_resultados(dados.resultados)

        dados_dict = dados.model_dump(exclude_unset=True, exclude={"resultados"})
        self.repository.update(antibiograma, dados_dict)

        if dados.resultados is not None:
            self.repository.definir_resultados(
                antibiograma_id, [r.model_dump() for r in dados.resultados]
            )

        return self.repository.get_by_id(antibiograma_id)

    def liberar(self, antibiograma_id: uuid.UUID):
        antibiograma = self.obter(antibiograma_id)
        if antibiograma.data_liberacao:
            raise BusinessRuleError("Este antibiograma já foi liberado.")
        if not antibiograma.resultados:
            raise BusinessRuleError(
                "Não é possível liberar um antibiograma sem nenhum resultado."
            )

        self.repository.update(
            antibiograma, {"data_liberacao": datetime.now(timezone.utc)}
        )
        return self.repository.get_by_id(antibiograma_id)

    def remover(self, antibiograma_id: uuid.UUID):
        antibiograma = self.obter(antibiograma_id)
        self.repository.soft_delete(antibiograma)
