"""
Router do catálogo de Microrganismos (base de conhecimento).
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.response import success_response
from app.db.session import get_db
from app.schemas.microrganismo import (
    MicrorganismoCreate,
    MicrorganismoOut,
    MicrorganismoUpdate,
)
from app.services.microrganismo_service import MicrorganismoService

router = APIRouter(
    prefix="/api/microrganismos",
    tags=["Microrganismos"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
def listar_microrganismos(
    termo: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = MicrorganismoService(db)
    items, total = service.listar(termo, page=page, page_size=page_size)
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            MicrorganismoOut.model_validate(item).model_dump(mode="json") for item in items
        ],
    }
    return success_response(data, message="Microrganismos listados com sucesso.")


@router.get("/{microrganismo_id}")
def obter_microrganismo(microrganismo_id: uuid.UUID, db: Session = Depends(get_db)):
    service = MicrorganismoService(db)
    microrganismo = service.obter(microrganismo_id)
    return success_response(
        MicrorganismoOut.model_validate(microrganismo).model_dump(mode="json"),
        message="Microrganismo encontrado.",
    )


@router.post("", status_code=201)
def criar_microrganismo(dados: MicrorganismoCreate, db: Session = Depends(get_db)):
    service = MicrorganismoService(db)
    microrganismo = service.criar(dados)
    return success_response(
        MicrorganismoOut.model_validate(microrganismo).model_dump(mode="json"),
        message="Microrganismo cadastrado com sucesso.",
    )


@router.put("/{microrganismo_id}")
def atualizar_microrganismo(
    microrganismo_id: uuid.UUID, dados: MicrorganismoUpdate, db: Session = Depends(get_db)
):
    service = MicrorganismoService(db)
    microrganismo = service.atualizar(microrganismo_id, dados)
    return success_response(
        MicrorganismoOut.model_validate(microrganismo).model_dump(mode="json"),
        message="Microrganismo atualizado com sucesso.",
    )


@router.delete("/{microrganismo_id}")
def remover_microrganismo(microrganismo_id: uuid.UUID, db: Session = Depends(get_db)):
    service = MicrorganismoService(db)
    service.remover(microrganismo_id)
    return success_response(message="Microrganismo removido com sucesso.")
