export interface Setor {
  id: string;
  nome: string;
  descricao: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SetorListagem {
  total: number;
  items: Setor[];
}

export interface SetorFormData {
  nome: string;
  descricao?: string | null;
}
