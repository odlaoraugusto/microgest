"""
Schema de saída do Dashboard.
"""
from pydantic import BaseModel


class TopMicrorganismoOut(BaseModel):
    nome: str
    quantidade: int


class AlertaOut(BaseModel):
    tipo: str  # "prazo" | "resistencia" | "info"
    mensagem: str


class ResumoDashboardOut(BaseModel):
    culturas_hoje: int
    aguardando_atualizacao: int
    prazo_vencido: int
    liberados_hoje: int
    top_microrganismos: list[TopMicrorganismoOut]
    alertas: list[AlertaOut]
