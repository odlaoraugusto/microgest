"""
Repository do Dashboard.

Concentra consultas agregadas (contagens, agrupamentos) usadas para
montar o resumo do Dashboard (Sprint 8). Não segue o padrão de
BaseRepository porque não representa uma entidade única, e sim uma
combinação de leituras sobre várias tabelas.
"""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.cultura import Cultura, CulturaMicrorganismo, ResultadoCulturaEnum
from app.models.microrganismo import Microrganismo
from app.models.solicitacao import Solicitacao, StatusSolicitacaoEnum
from app.repositories.parametro_sistema_repository import ParametroSistemaRepository

STATUS_EM_ANDAMENTO = (
    StatusSolicitacaoEnum.AGUARDANDO_COLETA,
    StatusSolicitacaoEnum.COLETADO,
    StatusSolicitacaoEnum.EM_ANALISE,
)

# Valor de fallback caso o parâmetro "prazo_solicitacao_dias" ainda não
# tenha sido semeado no banco (ex.: testes que criam schema sem migração).
PRAZO_PADRAO_DIAS_FALLBACK = 2


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def _hoje_utc(self) -> date:
        return datetime.now(timezone.utc).date()

    def contar_culturas_criadas_hoje(self) -> int:
        hoje = self._hoje_utc()
        stmt = select(func.count(Cultura.id)).where(
            Cultura.is_active.is_(True), func.date(Cultura.created_at) == hoje
        )
        return self.db.scalar(stmt) or 0

    def contar_solicitacoes_em_andamento(self) -> int:
        stmt = select(func.count(Solicitacao.id)).where(
            Solicitacao.is_active.is_(True),
            Solicitacao.status.in_(STATUS_EM_ANDAMENTO),
        )
        return self.db.scalar(stmt) or 0

    def contar_solicitacoes_com_prazo_vencido(self) -> int:
        prazo_dias = ParametroSistemaRepository(self.db).get_valor_int(
            "prazo_solicitacao_dias", PRAZO_PADRAO_DIAS_FALLBACK
        )
        limite = self._hoje_utc() - timedelta(days=prazo_dias)
        stmt = select(func.count(Solicitacao.id)).where(
            Solicitacao.is_active.is_(True),
            Solicitacao.status.in_(STATUS_EM_ANDAMENTO),
            Solicitacao.data_solicitacao <= limite,
        )
        return self.db.scalar(stmt) or 0

    def contar_culturas_liberadas_hoje(self) -> int:
        hoje = self._hoje_utc()
        stmt = select(func.count(Cultura.id)).where(
            Cultura.is_active.is_(True),
            Cultura.liberado_tecnicamente.is_(True),
            func.date(Cultura.data_liberacao) == hoje,
        )
        return self.db.scalar(stmt) or 0

    def top_microrganismos(self, dias: int = 30, limite: int = 5) -> list[tuple[str, int]]:
        desde = datetime.now(timezone.utc) - timedelta(days=dias)
        stmt = (
            select(Microrganismo.nome, func.count(CulturaMicrorganismo.id).label("qtd"))
            .join(
                CulturaMicrorganismo,
                CulturaMicrorganismo.microrganismo_id == Microrganismo.id,
            )
            .join(Cultura, Cultura.id == CulturaMicrorganismo.cultura_id)
            .where(Cultura.is_active.is_(True), Cultura.created_at >= desde)
            .group_by(Microrganismo.nome)
            .order_by(func.count(CulturaMicrorganismo.id).desc())
            .limit(limite)
        )
        return list(self.db.execute(stmt).all())

    def culturas_positivas_aguardando_liberacao(self) -> int:
        stmt = select(func.count(Cultura.id)).where(
            Cultura.is_active.is_(True),
            Cultura.resultado == ResultadoCulturaEnum.POSITIVA,
            Cultura.liberado_tecnicamente.is_(False),
        )
        return self.db.scalar(stmt) or 0
