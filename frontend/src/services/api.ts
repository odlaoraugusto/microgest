import axios, { AxiosError } from "axios";

export const TOKEN_STORAGE_KEY = "microgest_token";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Anexa o token JWT (quando existir) em toda requisição.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Se a sessão expirar/for inválida (401), limpa o token guardado.
// A navegação para a tela de login é feita pelo ProtectedRoute, que
// reage à ausência de token no próximo carregamento/consulta.
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
    }
    return Promise.reject(error);
  }
);

/**
 * Envelope de resposta padrão da API MicroGest, conforme o contrato
 * definido no Documento Mestre (seção 8 - Padrão da API).
 */
export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface ApiErrorResponse {
  success: false;
  message: string;
  errors: string[];
}

/**
 * Extrai a mensagem de erro do contrato padrão da API a partir de um erro
 * do axios, sem precisar tipar o catch como `any`.
 */
export function extrairMensagemErro(err: unknown, fallback: string): string {
  if (axios.isAxiosError(err)) {
    const mensagem = (err.response?.data as { message?: string } | undefined)?.message;
    if (mensagem) return mensagem;
  }
  return fallback;
}
