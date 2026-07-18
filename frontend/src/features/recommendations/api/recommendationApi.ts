import { apiClient } from "@/lib/axios";
import type { ApiList, MutationMessage, Recommendation } from "@/types/api";

export async function fetchRecommendations() {
  const { data } = await apiClient.get<ApiList<Recommendation>>("/recommendations");
  return data;
}

export async function refreshRecommendations() {
  const { data } = await apiClient.get<ApiList<Recommendation>>("/recommendations/refresh");
  return data;
}

export async function clearRecommendations() {
  const { data } = await apiClient.delete<{ deleted: number }>("/recommendations");
  return data;
}

export async function dismissRecommendation(id: number) {
  const { data } = await apiClient.delete<MutationMessage & { deleted: number }>(`/recommendations/${id}`);
  return data;
}
