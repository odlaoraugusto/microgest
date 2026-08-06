"""
Repository do módulo Culturas.

Lida também com a tabela de associação CulturaMicrorganismo, já que a
listagem/edição de uma cultura sempre acompanha os microrganismos
isolados.
"""
import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, joinedload

from app.models.antibiograma import Antibiograma, AntibiogramaResultado
from app.models.cultura import Cultura, CulturaMicrorganismo, GrupoCulturaEnum, ResultadoCulturaEnum
from app.repositories.base import BaseRepository


class CulturaRepository(BaseRepository[Cultura]):
    def __init__(self, db: Session):
        super().__init__(db, Cultura)

    def get_by_id(self, entity_id: uuid.UUID) -> Cultura | None:
        stmt = (
            select(Cultura)
            .options(
                joinedload(Cultura.solicitacao),
                joinedload(Cultura.microrganismos).joinedload(
                    CulturaMicrorganismo.microrganismo
                ),
            )
            .where(Cultura.id == entity_id)
        )
        return self.db.scalars(stmt).unique().first()

    def search(
        self,
        solicitacao_id: uuid.UUID | None = None,
        resultado: ResultadoCulturaEnum | None = None,
        grupo: GrupoCulturaEnum | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Cultura], int]:
        stmt = (
            select(Cultura)
            .options(
                joinedload(Cultura.solicitacao),
                joinedload(Cultura.microrganismos).joinedload(
                    CulturaMicrorganismo.microrganismo
                ),
            )
            .where(Cultura.is_active.is_(True))
        )

        if solicitacao_id:
            stmt = stmt.where(Cultura.solicitacao_id == solicitacao_id)
        if resultado:
            stmt = stmt.where(Cultura.resultado == resultado)
        if grupo:
            stmt = stmt.where(Cultura.grupo == grupo)

        total = len(self.db.scalars(stmt).unique().all())
        items = (
            self.db.scalars(
                stmt.offset(skip).limit(limit).order_by(Cultura.created_at.desc())
            )
            .unique()
            .all()
        )
        return list(items), total

    def definir_microrganismos(self, cultura_id: uuid.UUID, microrganismo_ids: list[uuid.UUID]):
        """Substitui a lista de microrganismos isolados na cultura."""
        self.db.execute(
            delete(CulturaMicrorganismo).where(
                CulturaMicrorganismo.cultura_id == cultura_id
            )
        )
        for microrganismo_id in microrganismo_ids:
            self.db.add(
                CulturaMicrorganismo(cultura_id=cultura_id, microrganismo_id=microrganismo_id)
            )
        self.db.commit()

    def isolados_sem_antibiograma(self, cultura: Cultura) -> list[uuid.UUID]:
        """
        Entre os isolados (CulturaMicrorganismo) de uma cultura, devolve os
        IDs dos que ainda não têm nenhum antibiograma com resultado
        preenchido - usado para bloquear a liberação de culturas positivas
        incompletas.

        Isolados marcados como "sem antibiograma padronizado (BrCAST)" são
        excluídos dessa lista - eles são dispensados individualmente da
        exigência de antibiograma (ex.: microrganismo sem protocolo BrCAST).
        """
        isolado_ids = [
            cm.id for cm in cultura.microrganismos if not cm.sem_antibiograma_padronizado
        ]
        if not isolado_ids:
            return []

        stmt = (
            select(CulturaMicrorganismo.id)
            .outerjoin(
                Antibiograma, Antibiograma.cultura_microrganismo_id == CulturaMicrorganismo.id
            )
            .outerjoin(
                AntibiogramaResultado,
                AntibiogramaResultado.antibiograma_id == Antibiograma.id,
            )
            .where(CulturaMicrorganismo.id.in_(isolado_ids))
            .group_by(CulturaMicrorganismo.id)
            .having(func.count(AntibiogramaResultado.id) == 0)
        )
        return list(self.db.scalars(stmt).all())

    def buscar_parciais(self) -> list[Cultura]:
        """
        Culturas ainda não liberadas tecnicamente - a base do "relatório de
        resultados parciais". Ordenadas pela previsão de liberação mais
        próxima primeiro (as mais urgentes no topo).
        """
        stmt = (
            select(Cultura)
            .options(
                joinedload(Cultura.solicitacao),
                joinedload(Cultura.microrganismos).joinedload(
                    CulturaMicrorganismo.microrganismo
                ),
            )
            .where(Cultura.is_active.is_(True), Cultura.liberado_tecnicamente.is_(False))
            .order_by(Cultura.previsao_liberacao.asc().nulls_last(), Cultura.created_at.asc())
        )
        return list(self.db.scalars(stmt).unique().all())
