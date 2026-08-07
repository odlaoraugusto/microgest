export type Gram = "POSITIVO" | "NEGATIVO" | "NAO_SE_APLICA";

export type TipoMicrorganismo =
  | "BACTERIA"
  | "FUNGO"
  | "MICOBACTERIA"
  | "VIRUS"
  | "PARASITA"
  | "OUTRO";

export type Morfologia = "COCO" | "BACILO" | "COCOBACILO" | "LEVEDURA" | "NAO_SE_APLICA";

export interface Microrganismo {
  id: string;
  nome: string;
  nome_cientifico: string | null;
  gram: Gram;
  tipo: TipoMicrorganismo;
  morfologia: Morfologia;
  fermentador: boolean | null;
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
  // gram/tipo/morfologia/fermentador/familia são opcionais de propósito: se
  // nenhum for enviado, o backend tenta herdar a taxonomia de outro
  // microrganismo já cadastrado do mesmo gênero (ver MicrorganismoService.
  // criar no backend) em vez de usar defaults genéricos - por isso o
  // cadastro rápido (MicrorganismoMultiSelect) não deve preencher nenhum
  // desses campos "à toa".
  gram?: Gram;
  tipo?: TipoMicrorganismo;
  morfologia?: Morfologia;
  fermentador?: boolean | null;
  familia?: string | null;
  relevancia_clinica?: string | null;
}
