"""
Router do módulo Solicitações.
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.response import success_response
from app.db.session import get_db
from app.models.solicitacao import StatusSolicitacaoEnum
from app.schemas.solicitacao import SolicitacaoCreate, SolicitacaoOut, SolicitacaoUpdate
from app.services.solicitacao_service import SolicitacaoService

router = APIRouter(
    prefix="/api/solicitacoes", tags=["Solicitações"], dependencies=[Depends(get_current_user)]
)


@router.get("")
def listar_solicitacoes(
    paciente_id: uuid.UUID | None = Query(default=None),
    status: StatusSolicitacaoEnum | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = SolicitacaoService(db)
    items, total = service.listar(paciente_id, status, page=page, page_size=page_size)
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            SolicitacaoOut.model_validate(item).model_dump(mode="json") for item in items
        ],
    }
    return success_response(data, message="Solicitações listadas com sucesso.")


@router.get("/{solicitacao_id}")
def obter_solicitacao(solicitacao_id: uuid.UUID, db: Session = Depends(get_db)):
    service = SolicitacaoService(db)
    solicitacao = service.obter(solicitacao_id)
    return success_response(
        SolicitacaoOut.model_validate(solicitacao).model_dump(mode="json"),
        message="Solicitação encontrada.",
    )


@router.post("", status_code=201)
def criar_solicitacao(dados: SolicitacaoCreate, db: Session = Depends(get_db)):
    service = SolicitacaoService(db)
    solicitacao = service.criar(dados)
    return success_response(
        SolicitacaoOut.model_validate(solicitacao).model_dump(mode="json"),
        message="Solicitação cadastrada com sucesso.",
    )


@router.put("/{solicitacao_id}")
def atualizar_solicitacao(
    solicitacao_id: uuid.UUID, dados: SolicitacaoUpdate, db: Session = Depends(get_db)
):
    service = SolicitacaoService(db)
    solicitacao = service.atualizar(solicitacao_id, dados)
    return success_response(
        SolicitacaoOut.model_validate(solicitacao).model_dump(mode="json"),
        message="Solicitação atualizada com sucesso.",
    )


@router.delete("/{solicitacao_id}")
def remover_solicitacao(solicitacao_id: uuid.UUID, db: Session = Depends(get_db)):
    service = SolicitacaoService(db)
    service.remover(solicitacao_id)
    return success_response(message="Solicitação removida com sucesso.")
