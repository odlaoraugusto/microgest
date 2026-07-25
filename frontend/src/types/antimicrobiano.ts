export interface Antimicrobiano {
  id: string;
  nome: string;
  sigla: string | null;
  classe: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AntimicrobianoListagem {
  total: number;
  page: number;
  page_size: number;
  items: Antimicrobiano[];
}

export interface AntimicrobianoFormData {
  nome: string;
  sigla?: string | null;
  classe?: string | null;
}
