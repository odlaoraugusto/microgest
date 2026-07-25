"""
Repository do módulo Solicitações.

Além do CRUD genérico (herdado de BaseRepository), implementa filtros
por paciente e por status, usados no fluxo operacional do laboratório.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.solicitacao import Solicitacao, StatusSolicitacaoEnum
from app.repositories.base import BaseRepository


class SolicitacaoRepository(BaseRepository[Solicitacao]):
    def __init__(self, db: Session):
        super().__init__(db, Solicitacao)

    def get_by_id(self, entity_id: uuid.UUID) -> Solicitacao | None:
        stmt = (
            select(Solicitacao)
            .options(joinedload(Solicitacao.paciente))
            .where(Solicitacao.id == entity_id)
        )
        return self.db.scalars(stmt).first()

    def search(
        self,
        paciente_id: uuid.UUID | None = None,
        status: StatusSolicitacaoEnum | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Solicitacao], int]:
        stmt = (
            select(Solicitacao)
            .options(joinedload(Solicitacao.paciente))
            .where(Solicitacao.is_active.is_(True))
        )

        if paciente_id:
            stmt = stmt.where(Solicitacao.paciente_id == paciente_id)
        if status:
            stmt = stmt.where(Solicitacao.status == status)

        total = len(self.db.scalars(stmt).unique().all())
        items = (
            self.db.scalars(
                stmt.offset(skip).limit(limit).order_by(Solicitacao.created_at.desc())
            )
            .unique()
            .all()
        )
        return list(items), total
