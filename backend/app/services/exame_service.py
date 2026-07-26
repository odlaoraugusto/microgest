"""
Service do módulo Exames.

Não reimplementa nenhuma regra de negócio de Solicitações/Microbiologia -
apenas compõe `SolicitacaoService` e `CulturaService` para permitir
cadastrar um exame microbiológico completo (solicitação já coletada +
cultura) numa única operação, eliminando o retrabalho de 2 telas
sequenciais do fluxo atual (ver app.services.solicitacao_service e
app.services.cultura_service para as regras herdadas).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.cultura import ResultadoCulturaEnum
from app.models.solicitacao import StatusSolicitacaoEnum
from app.schemas.cultura import CulturaCreate, CulturaUpdate
from app.schemas.exame import ExameCreate, ExameUpdate
from app.schemas.solicitacao import SolicitacaoCreate, SolicitacaoUpdate
from app.services.cultura_service import CulturaService
from app.services.solicitacao_service import SolicitacaoService

# Campos de ExameCreate/ExameUpdate que pertencem à Solicitação e à
# Cultura, respectivamente - usados em `atualizar` para roteá-los ao
# service correto. Os nomes "observacoes_solicitacao"/"observacoes_cultura"
# existem só para desambiguar as duas origens no schema compartilhado;
# ambos mapeiam para o campo "observacoes" de cada entidade.
_CAMPOS_SOLICITACAO = {"material", "origem", "prioridade", "observacoes_solicitacao"}
_CAMPOS_CULTURA = {"resultado", "microrganismo_ids", "previsao_liberacao", "observacoes_cultura"}


class ExameService:
    def __init__(self, db: Session):
        self.solicitacao_service = SolicitacaoService(db)
        self.cultura_service = CulturaService(db)

    def listar(
        self,
        resultado: ResultadoCulturaEnum | None,
        page: int = 1,
        page_size: int = 20,
    ):
        return self.cultura_service.listar(None, resultado, page=page, page_size=page_size)

    def obter(self, cultura_id: uuid.UUID):
        return self.cultura_service.obter(cultura_id)

    def criar(self, dados: ExameCreate):
        # 1-2. Cria a solicitação já como COLETADO - o coração da mudança:
        # no fluxo real, a coleta já aconteceu antes de chegar ao MicroGest.
        solicitacao_dados = SolicitacaoCreate(
            paciente_id=dados.paciente_id,
            material=dados.material,
            origem=dados.origem,
            prioridade=dados.prioridade,
            status=StatusSolicitacaoEnum.COLETADO,
            data_coleta=datetime.now(timezone.utc),
            observacoes=dados.observacoes_solicitacao,
        )
        solicitacao = self.solicitacao_service.criar(solicitacao_dados)

        # 3-4. Cria a cultura vinculada, reaproveitando a validação de
        # microrganismos-só-se-positiva e o cálculo de previsão automática.
        cultura_dados = CulturaCreate(
            solicitacao_id=solicitacao.id,
            resultado=dados.resultado,
            observacoes=dados.observacoes_cultura,
            microrganismo_ids=dados.microrganismo_ids,
            previsao_liberacao=dados.previsao_liberacao,
        )
        return self.cultura_service.criar(cultura_dados)

    def atualizar(self, cultura_id: uuid.UUID, dados: ExameUpdate):
        cultura = self.cultura_service.obter(cultura_id)

        dados_dict = dados.model_dump(exclude_unset=True)

        solicitacao_updates = {k: v for k, v in dados_dict.items() if k in _CAMPOS_SOLICITACAO}
        if solicitacao_updates:
            if "observacoes_solicitacao" in solicitacao_updates:
                solicitacao_updates["observacoes"] = solicitacao_updates.pop(
                    "observacoes_solicitacao"
                )
            self.solicitacao_service.atualizar(
                cultura.solicitacao_id, SolicitacaoUpdate(**solicitacao_updates)
            )

        cultura_updates = {k: v for k, v in dados_dict.items() if k in _CAMPOS_CULTURA}
        if cultura_updates:
            if "observacoes_cultura" in cultura_updates:
                cultura_updates["observacoes"] = cultura_updates.pop("observacoes_cultura")
            self.cultura_service.atualizar(cultura_id, CulturaUpdate(**cultura_updates))

        return self.cultura_service.obter(cultura_id)

    def liberar(self, cultura_id: uuid.UUID):
        return self.cultura_service.liberar(cultura_id)

    def remover(self, cultura_id: uuid.UUID):
        self.cultura_service.remover(cultura_id)
