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
    origem: str | None = Query(default=None, description="Filtra por setor/origem da solicitação"),
    db: Session = Depends(get_db),
):
    """Indicadores gerais - todas as culturas, exceto as de vigilância."""
    service = CCIHService(db)
    indicadores = service.indicadores(data_inicio, data_fim, origem=origem)
    return success_response(
        indicadores.model_dump(mode="json"), message="Indicadores da CCIH calculados com sucesso."
    )


@router.get("/indicadores/vigilancia")
def obter_indicadores_ccih_vigilancia(
    data_inicio: date | None = Query(default=None),
    data_fim: date | None = Query(default=None),
    origem: str | None = Query(default=None, description="Filtra por setor/origem da solicitação"),
    db: Session = Depends(get_db),
):
    """Indicadores dedicados às culturas de vigilância (rastreio/colonização)."""
    service = CCIHService(db)
    indicadores = service.indicadores_vigilancia(data_inicio, data_fim, origem=origem)
    return success_response(
        indicadores.model_dump(mode="json"),
        message="Indicadores de vigilância calculados com sucesso.",
    )
