"""
Router do módulo Antibiogramas (Sprint 7).
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.response import success_response
from app.db.session import get_db
from app.schemas.antibiograma import AntibiogramaCreate, AntibiogramaOut, AntibiogramaUpdate
from app.services.antibiograma_service import AntibiogramaService

router = APIRouter(
    prefix="/api/antibiogramas", tags=["Antibiogramas"], dependencies=[Depends(get_current_user)]
)


@router.get("")
def listar_antibiogramas(
    cultura_microrganismo_id: uuid.UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = AntibiogramaService(db)
    items, total = service.listar(cultura_microrganismo_id, page=page, page_size=page_size)
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            AntibiogramaOut.model_validate(item).model_dump(mode="json") for item in items
        ],
    }
    return success_response(data, message="Antibiogramas listados com sucesso.")


@router.get("/{antibiograma_id}")
def obter_antibiograma(antibiograma_id: uuid.UUID, db: Session = Depends(get_db)):
    service = AntibiogramaService(db)
    antibiograma = service.obter(antibiograma_id)
    return success_response(
        AntibiogramaOut.model_validate(antibiograma).model_dump(mode="json"),
        message="Antibiograma encontrado.",
    )


@router.post("", status_code=201)
def criar_antibiograma(dados: AntibiogramaCreate, db: Session = Depends(get_db)):
    service = AntibiogramaService(db)
    antibiograma = service.criar(dados)
    return success_response(
        AntibiogramaOut.model_validate(antibiograma).model_dump(mode="json"),
        message="Antibiograma cadastrado com sucesso.",
    )


@router.put("/{antibiograma_id}")
def atualizar_antibiograma(
    antibiograma_id: uuid.UUID, dados: AntibiogramaUpdate, db: Session = Depends(get_db)
):
    service = AntibiogramaService(db)
    antibiograma = service.atualizar(antibiograma_id, dados)
    return success_response(
        AntibiogramaOut.model_validate(antibiograma).model_dump(mode="json"),
        message="Antibiograma atualizado com sucesso.",
    )


@router.post("/{antibiograma_id}/liberar")
def liberar_antibiograma(antibiograma_id: uuid.UUID, db: Session = Depends(get_db)):
    service = AntibiogramaService(db)
    antibiograma = service.liberar(antibiograma_id)
    return success_response(
        AntibiogramaOut.model_validate(antibiograma).model_dump(mode="json"),
        message="Antibiograma liberado com sucesso.",
    )


@router.delete("/{antibiograma_id}")
def remover_antibiograma(antibiograma_id: uuid.UUID, db: Session = Depends(get_db)):
    service = AntibiogramaService(db)
    service.remover(antibiograma_id)
    return success_response(message="Antibiograma removido com sucesso.")
