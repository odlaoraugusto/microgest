import { api, ApiResponse } from "./api";
import {
  Microrganismo,
  MicrorganismoFormData,
  MicrorganismoListagem,
} from "../types/microrganismo";

export async function listarMicrorganismos(
  termo?: string,
  page = 1,
  pageSize = 50
): Promise<MicrorganismoListagem> {
  const response = await api.get<ApiResponse<MicrorganismoListagem>>(
    "/api/microrganismos",
    { params: { termo, page, page_size: pageSize } }
  );
  return response.data.data;
}

export async function criarMicrorganismo(
  dados: MicrorganismoFormData
): Promise<Microrganismo> {
  const response = await api.post<ApiResponse<Microrganismo>>(
    "/api/microrganismos",
    dados
  );
  return response.data.data;
}

export async function atualizarMicrorganismo(
  id: string,
  dados: Partial<MicrorganismoFormData>
): Promise<Microrganismo> {
  const response = await api.put<ApiResponse<Microrganismo>>(
    `/api/microrganismos/${id}`,
    dados
  );
  return response.data.data;
}

export async function removerMicrorganismo(id: string): Promise<void> {
  await api.delete(`/api/microrganismos/${id}`);
}
