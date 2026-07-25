"""
Router do catálogo de Setores (Sprint 11).
"""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.response import success_response
from app.db.session import get_db
from app.schemas.setor import SetorCreate, SetorOut, SetorUpdate
from app.services.setor_service import SetorService

router = APIRouter(
    prefix="/api/setores", tags=["Setores"], dependencies=[Depends(get_current_user)]
)


@router.get("")
def listar_setores(db: Session = Depends(get_db)):
    service = SetorService(db)
    itens = service.listar()
    data = {"total": len(itens), "items": [SetorOut.model_validate(i).model_dump(mode="json") for i in itens]}
    return success_response(data, message="Setores listados com sucesso.")


@router.post("", status_code=201)
def criar_setor(dados: SetorCreate, db: Session = Depends(get_db)):
    service = SetorService(db)
    setor = service.criar(dados)
    return success_response(
        SetorOut.model_validate(setor).model_dump(mode="json"), message="Setor cadastrado com sucesso."
    )


@router.put("/{setor_id}")
def atualizar_setor(setor_id: uuid.UUID, dados: SetorUpdate, db: Session = Depends(get_db)):
    service = SetorService(db)
    setor = service.atualizar(setor_id, dados)
    return success_response(
        SetorOut.model_validate(setor).model_dump(mode="json"), message="Setor atualizado com sucesso."
    )


@router.delete("/{setor_id}")
def remover_setor(setor_id: uuid.UUID, db: Session = Depends(get_db)):
    service = SetorService(db)
    service.remover(setor_id)
    return success_response(message="Setor removido com sucesso.")
