"""
Router do catálogo de Antimicrobianos.
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.response import success_response
from app.db.session import get_db
from app.schemas.antimicrobiano import (
    AntimicrobianoCreate,
    AntimicrobianoOut,
    AntimicrobianoUpdate,
)
from app.services.antimicrobiano_service import AntimicrobianoService

router = APIRouter(
    prefix="/api/antimicrobianos",
    tags=["Antimicrobianos"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
def listar_antimicrobianos(
    termo: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = AntimicrobianoService(db)
    items, total = service.listar(termo, page=page, page_size=page_size)
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            AntimicrobianoOut.model_validate(item).model_dump(mode="json") for item in items
        ],
    }
    return success_response(data, message="Antimicrobianos listados com sucesso.")


@router.get("/{antimicrobiano_id}")
def obter_antimicrobiano(antimicrobiano_id: uuid.UUID, db: Session = Depends(get_db)):
    service = AntimicrobianoService(db)
    antimicrobiano = service.obter(antimicrobiano_id)
    return success_response(
        AntimicrobianoOut.model_validate(antimicrobiano).model_dump(mode="json"),
        message="Antimicrobiano encontrado.",
    )


@router.post("", status_code=201)
def criar_antimicrobiano(dados: AntimicrobianoCreate, db: Session = Depends(get_db)):
    service = AntimicrobianoService(db)
    antimicrobiano = service.criar(dados)
    return success_response(
        AntimicrobianoOut.model_validate(antimicrobiano).model_dump(mode="json"),
        message="Antimicrobiano cadastrado com sucesso.",
    )


@router.put("/{antimicrobiano_id}")
def atualizar_antimicrobiano(
    antimicrobiano_id: uuid.UUID, dados: AntimicrobianoUpdate, db: Session = Depends(get_db)
):
    service = AntimicrobianoService(db)
    antimicrobiano = service.atualizar(antimicrobiano_id, dados)
    return success_response(
        AntimicrobianoOut.model_validate(antimicrobiano).model_dump(mode="json"),
        message="Antimicrobiano atualizado com sucesso.",
    )


@router.delete("/{antimicrobiano_id}")
def remover_antimicrobiano(antimicrobiano_id: uuid.UUID, db: Session = Depends(get_db)):
    service = AntimicrobianoService(db)
    service.remover(antimicrobiano_id)
    return success_response(message="Antimicrobiano removido com sucesso.")
