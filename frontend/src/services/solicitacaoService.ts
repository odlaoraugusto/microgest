import { api, ApiResponse } from "./api";
import {
  Solicitacao,
  SolicitacaoFormData,
  SolicitacaoListagem,
  StatusSolicitacao,
} from "../types/solicitacao";

export async function listarSolicitacoes(
  pacienteId?: string,
  status?: StatusSolicitacao,
  page = 1,
  pageSize = 20
): Promise<SolicitacaoListagem> {
  const response = await api.get<ApiResponse<SolicitacaoListagem>>("/api/solicitacoes", {
    params: { paciente_id: pacienteId, status, page, page_size: pageSize },
  });
  return response.data.data;
}

export async function obterSolicitacao(id: string): Promise<Solicitacao> {
  const response = await api.get<ApiResponse<Solicitacao>>(`/api/solicitacoes/${id}`);
  return response.data.data;
}

export async function criarSolicitacao(
  dados: SolicitacaoFormData
): Promise<Solicitacao> {
  const response = await api.post<ApiResponse<Solicitacao>>("/api/solicitacoes", dados);
  return response.data.data;
}

export async function atualizarSolicitacao(
  id: string,
  dados: Partial<SolicitacaoFormData>
): Promise<Solicitacao> {
  const response = await api.put<ApiResponse<Solicitacao>>(
    `/api/solicitacoes/${id}`,
    dados
  );
  return response.data.data;
}

export async function removerSolicitacao(id: string): Promise<void> {
  await api.delete(`/api/solicitacoes/${id}`);
}
