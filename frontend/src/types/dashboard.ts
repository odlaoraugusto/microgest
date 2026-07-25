export interface TopMicrorganismo {
  nome: string;
  quantidade: number;
}

export type TipoAlerta = "prazo" | "resistencia" | "info";

export interface Alerta {
  tipo: TipoAlerta;
  mensagem: string;
}

export interface ResumoDashboard {
  culturas_hoje: number;
  aguardando_atualizacao: number;
  prazo_vencido: number;
  liberados_hoje: number;
  top_microrganismos: TopMicrorganismo[];
  alertas: Alerta[];
}
