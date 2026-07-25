import { api, ApiResponse } from "./api";
import { LogAuditoriaListagem } from "../types/auditoria";

export async function listarLogsAuditoria(
  page = 1,
  pageSize = 20
): Promise<LogAuditoriaListagem> {
  const response = await api.get<ApiResponse<LogAuditoriaListagem>>("/api/auditoria/logs", {
    params: { page, page_size: pageSize },
  });
  return response.data.data;
}
