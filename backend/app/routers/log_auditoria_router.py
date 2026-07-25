"""
Router de Logs de Auditoria (Sprint 13). Restrito a ADMIN.
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_perfil
from app.core.response import success_response
from app.db.session import get_db
from app.models.usuario import PerfilUsuarioEnum
from app.schemas.log_auditoria import LogAuditoriaOut
from app.services.log_auditoria_service import LogAuditoriaService

router = APIRouter(
    prefix="/api/auditoria",
    tags=["Auditoria"],
    dependencies=[Depends(require_perfil(PerfilUsuarioEnum.ADMIN))],
)


@router.get("/logs")
def listar_logs(
    usuario_id: uuid.UUID | None = Query(default=None),
    metodo: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = LogAuditoriaService(db)
    items, total = service.listar(usuario_id, metodo, page=page, page_size=page_size)
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [LogAuditoriaOut.model_validate(item).model_dump(mode="json") for item in items],
    }
    return success_response(data, message="Logs de auditoria listados com sucesso.")
