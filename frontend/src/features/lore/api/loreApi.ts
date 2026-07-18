import { apiClient } from "@/lib/axios";
import type { Lore, LoreInput, MutationMessage } from "@/types/api";

export async function fetchLore() {
  const { data } = await apiClient.get<Lore[]>("/lore/");
  return data;
}

export async function fetchLoreById(id: string) {
  const { data } = await apiClient.get<Lore>(`/lore/${id}`);
  return data;
}

export async function createLore(payload: LoreInput) {
  const { data } = await apiClient.post<Lore>("/lore/", {
    ...payload,
    profession: payload.profession ?? "",
  });
  return data;
}

export async function updateLore(id: number, payload: Partial<LoreInput>) {
  const { data } = await apiClient.put<Lore>(`/lore/${id}`, {
    ...payload,
    profession: payload.profession ?? "",
  });
  return data;
}

export async function deleteLore(id: number) {
  const { data } = await apiClient.delete<MutationMessage>(`/lore/${id}`);
  return data;
}
