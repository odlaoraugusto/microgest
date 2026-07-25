import { api, ApiResponse } from "./api";
import { Antibiograma, AntibiogramaFormData, AntibiogramaListagem } from "../types/antibiograma";

export async function listarAntibiogramas(
  page = 1,
  pageSize = 20
): Promise<AntibiogramaListagem> {
  const response = await api.get<ApiResponse<AntibiogramaListagem>>("/api/antibiogramas", {
    params: { page, page_size: pageSize },
  });
  return response.data.data;
}

export async function obterAntibiograma(id: string): Promise<Antibiograma> {
  const response = await api.get<ApiResponse<Antibiograma>>(`/api/antibiogramas/${id}`);
  return response.data.data;
}

export async function criarAntibiograma(
  dados: AntibiogramaFormData
): Promise<Antibiograma> {
  const response = await api.post<ApiResponse<Antibiograma>>("/api/antibiogramas", dados);
  return response.data.data;
}

export async function atualizarAntibiograma(
  id: string,
  dados: Partial<AntibiogramaFormData>
): Promise<Antibiograma> {
  const response = await api.put<ApiResponse<Antibiograma>>(
    `/api/antibiogramas/${id}`,
    dados
  );
  return response.data.data;
}

export async function liberarAntibiograma(id: string): Promise<Antibiograma> {
  const response = await api.post<ApiResponse<Antibiograma>>(
    `/api/antibiogramas/${id}/liberar`
  );
  return response.data.data;
}

export async function removerAntibiograma(id: string): Promise<void> {
  await api.delete(`/api/antibiogramas/${id}`);
}
