"""
Repository de Logs de Auditoria.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.log_auditoria import LogAuditoria


class LogAuditoriaRepository:
    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        usuario_id: uuid.UUID | None = None,
        metodo: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[LogAuditoria], int]:
        stmt = select(LogAuditoria)

        if usuario_id:
            stmt = stmt.where(LogAuditoria.usuario_id == usuario_id)
        if metodo:
            stmt = stmt.where(LogAuditoria.metodo == metodo.upper())

        total = len(self.db.scalars(stmt).all())
        items = (
            self.db.scalars(
                stmt.offset(skip).limit(limit).order_by(LogAuditoria.criado_em.desc())
            )
            .all()
        )
        return list(items), total
