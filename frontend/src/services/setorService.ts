import { api, ApiResponse } from "./api";
import { Setor, SetorFormData, SetorListagem } from "../types/setor";

export async function listarSetores(): Promise<SetorListagem> {
  const response = await api.get<ApiResponse<SetorListagem>>("/api/setores");
  return response.data.data;
}

export async function criarSetor(dados: SetorFormData): Promise<Setor> {
  const response = await api.post<ApiResponse<Setor>>("/api/setores", dados);
  return response.data.data;
}

export async function atualizarSetor(id: string, dados: Partial<SetorFormData>): Promise<Setor> {
  const response = await api.put<ApiResponse<Setor>>(`/api/setores/${id}`, dados);
  return response.data.data;
}

export async function removerSetor(id: string): Promise<void> {
  await api.delete(`/api/setores/${id}`);
}
