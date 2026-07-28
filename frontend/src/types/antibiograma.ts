import { Antimicrobiano } from "./antimicrobiano";
import { Microrganismo } from "./microrganismo";

export type ResultadoSIR = "SENSIVEL" | "INTERMEDIARIO" | "RESISTENTE";

// Rótulo exibido para cada resultado S/I/R. O valor "INTERMEDIARIO" continua
// sendo o código interno (banco/API), mas a terminologia clínica atual (CLSI)
// chama essa categoria de "Sensível, aumentando exposição" em vez de
// "Intermediário" - só o texto mostrado ao usuário muda.
export const RESULTADO_SIR_LABELS: Record<ResultadoSIR, string> = {
  SENSIVEL: "Sensível (S)",
  INTERMEDIARIO: "Sensível, aumentando exposição (I)",
  RESISTENTE: "Resistente (R)",
};

export interface ResultadoAntimicrobiano {
  antimicrobiano_id: string;
  resultado: ResultadoSIR;
}

export interface AntibiogramaResultado {
  antimicrobiano: Antimicrobiano;
  resultado: ResultadoSIR;
}

export interface CulturaMicrorganismoResumo {
  id: string;
  microrganismo: Microrganismo;
}

export interface Antibiograma {
  id: string;
  cultura_microrganismo_id: string;
  cultura_microrganismo: CulturaMicrorganismoResumo | null;
  data_liberacao: string | null;
  observacoes: string | null;
  resultados: AntibiogramaResultado[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AntibiogramaListagem {
  total: number;
  page: number;
  page_size: number;
  items: Antibiograma[];
}

export interface AntibiogramaFormData {
  cultura_microrganismo_id: string;
  observacoes?: string | null;
  resultados: ResultadoAntimicrobiano[];
}
