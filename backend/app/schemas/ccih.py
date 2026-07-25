"""
Schemas de saída do módulo CCIH (Comissão de Controle de Infecção
Hospitalar) - Documento Mestre, seção 6 (Sprint 9).
"""
from datetime import date

from pydantic import BaseModel


class DistribuicaoSetorOut(BaseModel):
    setor: str
    total_positivas: int


class PerfilMicrobiologicoOut(BaseModel):
    microrganismo: str
    quantidade: int
    percentual: float


class TaxaResistenciaOut(BaseModel):
    antimicrobiano: str
    total_testado: int
    total_resistente: int
    percentual_resistente: float


class IndicadoresCCIHOut(BaseModel):
    periodo_inicio: date
    periodo_fim: date
    total_solicitacoes: int
    total_culturas_positivas: int
    taxa_positividade: float
    distribuicao_por_setor: list[DistribuicaoSetorOut]
    perfil_microbiologico: list[PerfilMicrobiologicoOut]
    taxa_resistencia: list[TaxaResistenciaOut]
