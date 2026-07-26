import { api, ApiResponse } from "./api";
import { Cultura, CulturaListagem, ResultadoCultura } from "../types/cultura";
import { ExameFormData } from "../types/exame";

export async function listarExames(
  resultado?: ResultadoCultura,
  page = 1,
  pageSize = 20
): Promise<CulturaListagem> {
  const response = await api.get<ApiResponse<CulturaListagem>>("/api/exames", {
    params: { resultado, page, page_size: pageSize },
  });
  return response.data.data;
}

export async function obterExame(id: string): Promise<Cultura> {
  const response = await api.get<ApiResponse<Cultura>>(`/api/exames/${id}`);
  return response.data.data;
}

export async function criarExame(dados: ExameFormData): Promise<Cultura> {
  const response = await api.post<ApiResponse<Cultura>>("/api/exames", dados);
  return response.data.data;
}

export async function atualizarExame(
  id: string,
  dados: Partial<ExameFormData>
): Promise<Cultura> {
  const response = await api.put<ApiResponse<Cultura>>(`/api/exames/${id}`, dados);
  return response.data.data;
}

export async function liberarExame(id: string): Promise<Cultura> {
  const response = await api.post<ApiResponse<Cultura>>(`/api/exames/${id}/liberar`);
  return response.data.data;
}

export async function removerExame(id: string): Promise<void> {
  await api.delete(`/api/exames/${id}`);
}
