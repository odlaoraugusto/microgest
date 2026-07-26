"""
Router do módulo Exames.

Camada aditiva que permite cadastrar um exame microbiológico completo
(solicitação já coletada + cultura) numa única chamada, eliminando as
2 telas sequenciais do fluxo atual (Solicitações -> editar status ->
Microbiologia). Os módulos Solicitações/Microbiologia continuam
existindo intactos para o caso raro de agendamento antecipado.
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.response import success_response
from app.db.session import get_db
from app.models.cultura import ResultadoCulturaEnum
from app.schemas.cultura import CulturaOut
from app.schemas.exame import ExameCreate, ExameUpdate
from app.services.exame_service import ExameService

router = APIRouter(prefix="/api/exames", tags=["Exames"], dependencies=[Depends(get_current_user)])


@router.get("")
def listar_exames(
    resultado: ResultadoCulturaEnum | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ExameService(db)
    items, total = service.listar(resultado, page=page, page_size=page_size)
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [CulturaOut.model_validate(item).model_dump(mode="json") for item in items],
    }
    return success_response(data, message="Exames listados com sucesso.")


@router.get("/{cultura_id}")
def obter_exame(cultura_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ExameService(db)
    cultura = service.obter(cultura_id)
    return success_response(
        CulturaOut.model_validate(cultura).model_dump(mode="json"),
        message="Exame encontrado.",
    )


@router.post("", status_code=201)
def criar_exame(dados: ExameCreate, db: Session = Depends(get_db)):
    service = ExameService(db)
    cultura = service.criar(dados)
    return success_response(
        CulturaOut.model_validate(cultura).model_dump(mode="json"),
        message="Exame cadastrado com sucesso.",
    )


@router.put("/{cultura_id}")
def atualizar_exame(cultura_id: uuid.UUID, dados: ExameUpdate, db: Session = Depends(get_db)):
    service = ExameService(db)
    cultura = service.atualizar(cultura_id, dados)
    return success_response(
        CulturaOut.model_validate(cultura).model_dump(mode="json"),
        message="Exame atualizado com sucesso.",
    )


@router.post("/{cultura_id}/liberar")
def liberar_exame(cultura_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ExameService(db)
    cultura = service.liberar(cultura_id)
    return success_response(
        CulturaOut.model_validate(cultura).model_dump(mode="json"),
        message="Exame liberado tecnicamente com sucesso.",
    )


@router.delete("/{cultura_id}")
def remover_exame(cultura_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ExameService(db)
    service.remover(cultura_id)
    return success_response(message="Exame removido com sucesso.")
