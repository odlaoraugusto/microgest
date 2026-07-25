"""
Service de Logs de Auditoria (Sprint 13).
"""
import uuid

from sqlalchemy.orm import Session

from app.repositories.log_auditoria_repository import LogAuditoriaRepository


class LogAuditoriaService:
    def __init__(self, db: Session):
        self.repository = LogAuditoriaRepository(db)

    def listar(
        self,
        usuario_id: uuid.UUID | None,
        metodo: str | None,
        page: int = 1,
        page_size: int = 20,
    ):
        skip = (page - 1) * page_size
        return self.repository.search(
            usuario_id=usuario_id, metodo=metodo, skip=skip, limit=page_size
        )
