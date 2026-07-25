import { api, ApiResponse } from "./api";
import { ResumoDashboard } from "../types/dashboard";

export async function obterResumoDashboard(): Promise<ResumoDashboard> {
  const response = await api.get<ApiResponse<ResumoDashboard>>("/api/dashboard/resumo");
  return response.data.data;
}
