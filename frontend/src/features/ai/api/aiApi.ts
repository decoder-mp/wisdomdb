import { apiClient } from "@/lib/axios";
import type { Lore } from "@/types/api";

export type DiscoverResponse = {
  query: string;
  count: number;
  results: Lore[];
};

export async function extractThemes(text: string) {
  const { data } = await apiClient.post<{ themes: string[] }>("/ai/extract-themes", { text });
  return data;
}

export async function summarizeText(text: string) {
  const { data } = await apiClient.post<{ summary: string }>("/ai/summarize", { text });
  return data;
}

export async function discoverLore(query: string) {
  const { data } = await apiClient.get<DiscoverResponse>("/ai/discover", { params: { query } });
  return data;
}

export async function discoverForMe() {
  const { data } = await apiClient.get<DiscoverResponse>("/ai/discover/me");
  return data;
}