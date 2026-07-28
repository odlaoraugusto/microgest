"""
Repository do módulo CCIH.

Todas as consultas aqui são agregações sobre Solicitações, Culturas,
Microrganismos e Antibiogramas já existentes - a CCIH não introduz
nenhuma tabela nova, apenas uma nova forma de olhar para os dados que
o laboratório já produz no dia a dia.
"""
from datetime import date, datetime, time, timezone

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.antibiograma import Antibiograma, AntibiogramaResultado, ResultadoSIREnum
from app.models.antimicrobiano import Antimicrobiano
from app.models.cultura import Cultura, CulturaMicrorganismo, ResultadoCulturaEnum
from app.models.microrganismo import Microrganismo
from app.models.solicitacao import Solicitacao

SETOR_NAO_INFORMADO = "Não informado"


def _inicio_periodo(dia: date) -> datetime:
    return datetime.combine(dia, time.min, tzinfo=timezone.utc)


def _fim_periodo(dia: date) -> datetime:
    return datetime.combine(dia, time.max, tzinfo=timezone.utc)


class CCIHRepository:
    def __init__(self, db: Session):
        self.db = db

    def total_solicitacoes(self, inicio: date, fim: date) -> int:
        stmt = select(func.count(Solicitacao.id)).where(
            Solicitacao.is_active.is_(True),
            Solicitacao.data_solicitacao >= inicio,
            Solicitacao.data_solicitacao <= fim,
        )
        return self.db.scalar(stmt) or 0

    def total_culturas_por_resultado(
        self, inicio: date, fim: date, resultado: ResultadoCulturaEnum | None = None
    ) -> int:
        stmt = select(func.count(Cultura.id)).where(
            Cultura.is_active.is_(True),
            Cultura.created_at >= _inicio_periodo(inicio),
            Cultura.created_at <= _fim_periodo(fim),
        )
        if resultado:
            stmt = stmt.where(Cultura.resultado == resultado)
        else:
            stmt = stmt.where(Cultura.resultado != ResultadoCulturaEnum.EM_ANALISE)
        return self.db.scalar(stmt) or 0

    def distribuicao_por_setor(self, inicio: date, fim: date) -> list[tuple[str, int]]:
        origem_normalizada = func.coalesce(Solicitacao.origem, SETOR_NAO_INFORMADO)
        stmt = (
            select(origem_normalizada, func.count(Cultura.id))
            .select_from(Cultura)
            .join(Solicitacao, Solicitacao.id == Cultura.solicitacao_id)
            .where(
                Cultura.is_active.is_(True),
                Cultura.resultado == ResultadoCulturaEnum.POSITIVA,
                Cultura.created_at >= _inicio_periodo(inicio),
                Cultura.created_at <= _fim_periodo(fim),
            )
            .group_by(origem_normalizada)
            .order_by(func.count(Cultura.id).desc())
        )
        return list(self.db.execute(stmt).all())

    def perfil_microbiologico(self, inicio: date, fim: date) -> list[tuple[str, int]]:
        stmt = (
            select(Microrganismo.nome, func.count(CulturaMicrorganismo.id))
            .select_from(CulturaMicrorganismo)
            .join(Microrganismo, Microrganismo.id == CulturaMicrorganismo.microrganismo_id)
            .join(Cultura, Cultura.id == CulturaMicrorganismo.cultura_id)
            .where(
                Cultura.is_active.is_(True),
                Cultura.resultado == ResultadoCulturaEnum.POSITIVA,
                Cultura.created_at >= _inicio_periodo(inicio),
                Cultura.created_at <= _fim_periodo(fim),
            )
            .group_by(Microrganismo.nome)
            .order_by(func.count(CulturaMicrorganismo.id).desc())
        )
        return list(self.db.execute(stmt).all())

    def taxa_resistencia(self, inicio: date, fim: date) -> list[tuple[str, int, int, int]]:
        total_testado = func.count(AntibiogramaResultado.id)
        total_resistente = func.sum(
            case((AntibiogramaResultado.resultado == ResultadoSIREnum.RESISTENTE, 1), else_=0)
        )
        total_sensivel = func.sum(
            case((AntibiogramaResultado.resultado == ResultadoSIREnum.SENSIVEL, 1), else_=0)
        )
        stmt = (
            select(Antimicrobiano.nome, total_testado, total_resistente, total_sensivel)
            .select_from(AntibiogramaResultado)
            .join(Antimicrobiano, Antimicrobiano.id == AntibiogramaResultado.antimicrobiano_id)
            .join(Antibiograma, Antibiograma.id == AntibiogramaResultado.antibiograma_id)
            .where(
                Antibiograma.is_active.is_(True),
                Antibiograma.created_at >= _inicio_periodo(inicio),
                Antibiograma.created_at <= _fim_periodo(fim),
            )
            .group_by(Antimicrobiano.nome)
            .order_by(total_testado.desc())
        )
        resultado = self.db.execute(stmt).all()
        return [
            (nome, testado, resistente or 0, sensivel or 0)
            for nome, testado, resistente, sensivel in resultado
        ]
