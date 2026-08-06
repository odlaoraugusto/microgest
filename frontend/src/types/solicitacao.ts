import { Paciente } from "./paciente";

export type Prioridade = "ROTINA" | "URGENTE" | "EMERGENCIA";

export type StatusSolicitacao =
  | "AGUARDANDO_COLETA"
  | "COLETADO"
  | "EM_ANALISE"
  | "LIBERADO"
  | "CANCELADO";

export interface Solicitacao {
  id: string;
  paciente_id: string;
  paciente: Paciente | null;
  material: string;
  origem: string | null;
  prioridade: Prioridade;
  status: StatusSolicitacao;
  data_solicitacao: string;
  data_coleta: string | null;
  observacoes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SolicitacaoListagem {
  total: number;
  page: number;
  page_size: number;
  items: Solicitacao[];
}

export interface SolicitacaoFormData {
  paciente_id: string;
  material: string;
  origem?: string | null;
  prioridade: Prioridade;
  status?: StatusSolicitacao;
  data_coleta?: string | null;
  observacoes?: string | null;
}
