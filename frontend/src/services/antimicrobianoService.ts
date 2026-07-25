import { api, ApiResponse } from "./api";
import {
  Antimicrobiano,
  AntimicrobianoFormData,
  AntimicrobianoListagem,
} from "../types/antimicrobiano";

export async function listarAntimicrobianos(
  termo?: string,
  page = 1,
  pageSize = 50
): Promise<AntimicrobianoListagem> {
  const response = await api.get<ApiResponse<AntimicrobianoListagem>>(
    "/api/antimicrobianos",
    { params: { termo, page, page_size: pageSize } }
  );
  return response.data.data;
}

export async function criarAntimicrobiano(
  dados: AntimicrobianoFormData
): Promise<Antimicrobiano> {
  const response = await api.post<ApiResponse<Antimicrobiano>>(
    "/api/antimicrobianos",
    dados
  );
  return response.data.data;
}

export async function atualizarAntimicrobiano(
  id: string,
  dados: Partial<AntimicrobianoFormData>
): Promise<Antimicrobiano> {
  const response = await api.put<ApiResponse<Antimicrobiano>>(
    `/api/antimicrobianos/${id}`,
    dados
  );
  return response.data.data;
}

export async function removerAntimicrobiano(id: string): Promise<void> {
  await api.delete(`/api/antimicrobianos/${id}`);
}
