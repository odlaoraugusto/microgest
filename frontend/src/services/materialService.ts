import { api, ApiResponse } from "./api";
import { Material, MaterialFormData, MaterialListagem } from "../types/material";

export async function listarMateriais(): Promise<MaterialListagem> {
  const response = await api.get<ApiResponse<MaterialListagem>>("/api/materiais");
  return response.data.data;
}

export async function criarMaterial(dados: MaterialFormData): Promise<Material> {
  const response = await api.post<ApiResponse<Material>>("/api/materiais", dados);
  return response.data.data;
}

export async function atualizarMaterial(id: string, dados: Partial<MaterialFormData>): Promise<Material> {
  const response = await api.put<ApiResponse<Material>>(`/api/materiais/${id}`, dados);
  return response.data.data;
}

export async function removerMaterial(id: string): Promise<void> {
  await api.delete(`/api/materiais/${id}`);
}
