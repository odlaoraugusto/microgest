import { Prioridade } from "./solicitacao";
import { ResultadoCultura } from "./cultura";

/**
 * Payload do módulo Exames: compõe Solicitação + Cultura numa única
 * operação (ver `services/exameService.ts`). A resposta da API reaproveita
 * o tipo `Cultura` (com `solicitacao` aninhada) - não há um "Exame" de
 * saída próprio.
 */
export interface ExameFormData {
  paciente_id: string;
  material: string;
  origem?: string | null;
  prioridade: Prioridade;
  observacoes_solicitacao?: string | null;
  resultado: ResultadoCultura;
  microrganismo_ids: string[];
  previsao_liberacao?: string | null;
  observacoes_cultura?: string | null;
}
