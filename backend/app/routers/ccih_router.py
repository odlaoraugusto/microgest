"""
Router do módulo CCIH (Sprint 9).
"""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.response import success_response
from app.db.session import get_db
from app.services.ccih_service import CCIHService

router = APIRouter(prefix="/api/ccih", tags=["CCIH"], dependencies=[Depends(get_current_user)])


@router.get("/indicadores")
def obter_indicadores_ccih(
    data_inicio: date | None = Query(default=None),
    data_fim: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = CCIHService(db)
    indicadores = service.indicadores(data_inicio, data_fim)
    return success_response(
        indicadores.model_dump(mode="json"), message="Indicadores da CCIH calculados com sucesso."
    )
