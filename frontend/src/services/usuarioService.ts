import { api, ApiResponse } from "./api";
import { Usuario, UsuarioFormData, UsuarioListagem, UsuarioUpdateData } from "../types/usuario";

export async function listarUsuarios(page = 1, pageSize = 50): Promise<UsuarioListagem> {
  const response = await api.get<ApiResponse<UsuarioListagem>>("/api/usuarios", {
    params: { page, page_size: pageSize },
  });
  return response.data.data;
}

export async function criarUsuario(dados: UsuarioFormData): Promise<Usuario> {
  const response = await api.post<ApiResponse<Usuario>>("/api/usuarios", dados);
  return response.data.data;
}

export async function atualizarUsuario(
  id: string,
  dados: UsuarioUpdateData
): Promise<Usuario> {
  const response = await api.put<ApiResponse<Usuario>>(`/api/usuarios/${id}`, dados);
  return response.data.data;
}

export async function removerUsuario(id: string): Promise<void> {
  await api.delete(`/api/usuarios/${id}`);
}
