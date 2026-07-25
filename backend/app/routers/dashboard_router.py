"""
Router do módulo Dashboard (Sprint 8).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.response import success_response
from app.db.session import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/api/dashboard", tags=["Dashboard"], dependencies=[Depends(get_current_user)]
)


@router.get("/resumo")
def resumo_dashboard(db: Session = Depends(get_db)):
    service = DashboardService(db)
    resumo = service.resumo()
    return success_response(resumo.model_dump(mode="json"), message="Resumo do dashboard.")
