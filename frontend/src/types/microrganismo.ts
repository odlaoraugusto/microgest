export type Gram = "POSITIVO" | "NEGATIVO" | "NAO_SE_APLICA";

export type TipoMicrorganismo =
  | "BACTERIA"
  | "FUNGO"
  | "MICOBACTERIA"
  | "VIRUS"
  | "PARASITA"
  | "OUTRO";

export interface Microrganismo {
  id: string;
  nome: string;
  nome_cientifico: string | null;
  gram: Gram;
  tipo: TipoMicrorganismo;
  familia: string | null;
  relevancia_clinica: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MicrorganismoListagem {
  total: number;
  page: number;
  page_size: number;
  items: Microrganismo[];
}

export interface MicrorganismoFormData {
  nome: string;
  nome_cientifico?: string | null;
  gram: Gram;
  tipo: TipoMicrorganismo;
  familia?: string | null;
  relevancia_clinica?: string | null;
}
