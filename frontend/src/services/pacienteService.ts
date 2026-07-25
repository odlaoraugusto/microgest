import { api, ApiResponse } from "./api";
import { Paciente, PacienteFormData, PacienteListagem } from "../types/paciente";

export async function listarPacientes(
  termo?: string,
  page = 1,
  pageSize = 20
): Promise<PacienteListagem> {
  const response = await api.get<ApiResponse<PacienteListagem>>("/api/pacientes", {
    params: { termo, page, page_size: pageSize },
  });
  return response.data.data;
}

export async function obterPaciente(id: string): Promise<Paciente> {
  const response = await api.get<ApiResponse<Paciente>>(`/api/pacientes/${id}`);
  return response.data.data;
}

export async function criarPaciente(dados: PacienteFormData): Promise<Paciente> {
  const response = await api.post<ApiResponse<Paciente>>("/api/pacientes", dados);
  return response.data.data;
}

export async function atualizarPaciente(
  id: string,
  dados: Partial<PacienteFormData>
): Promise<Paciente> {
  const response = await api.put<ApiResponse<Paciente>>(`/api/pacientes/${id}`, dados);
  return response.data.data;
}

export async function removerPaciente(id: string): Promise<void> {
  await api.delete(`/api/pacientes/${id}`);
}
