export interface Material {
  id: string;
  nome: string;
  descricao: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MaterialListagem {
  total: number;
  items: Material[];
}

export interface MaterialFormData {
  nome: string;
  descricao?: string | null;
}
