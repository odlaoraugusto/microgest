import { Solicitacao } from "./solicitacao";
import { Microrganismo } from "./microrganismo";

export type ResultadoCultura = "EM_ANALISE" | "POSITIVA" | "NEGATIVA" | "CONTAMINADA";

export type GrupoCultura = "HEMOCULTURA" | "CULTURA_GERAL" | "VIGILANCIA" | "BK" | "FUNGOS";

export interface CulturaMicrorganismo {
  id: string;
  microrganismo: Microrganismo;
  sem_antibiograma_padronizado: boolean;
}

export interface Cultura {
  id: string;
  solicitacao_id: string;
  solicitacao: Solicitacao | null;
  grupo: GrupoCultura;
  resultado: ResultadoCultura;
  liberado_tecnicamente: boolean;
  data_liberacao: string | null;
  previsao_liberacao: string | null;
  observacoes: string | null;
  microrganismos: CulturaMicrorganismo[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CulturaParcial extends Cultura {
  pendencia: string;
}

export interface CulturaParcialListagem {
  total: number;
  items: CulturaParcial[];
}

export interface CulturaListagem {
  total: number;
  page: number;
  page_size: number;
  items: Cultura[];
}

export interface CulturaFormData {
  solicitacao_id: string;
  grupo: GrupoCultura;
  resultado: ResultadoCultura;
  observacoes?: string | null;
  microrganismo_ids: string[];
  previsao_liberacao?: string | null;
}
