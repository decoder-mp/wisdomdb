import { apiClient } from "@/lib/axios";
import type { LikeCount, MutationMessage, Bookmark } from "@/types/api";

export async function fetchLikeCount(loreId: number) {
  const { data } = await apiClient.get<LikeCount>(`/likes/${loreId}`);
  return data;
}

export async function fetchMyLikes() {
  const { data } = await apiClient.get<Bookmark[]>("/likes/me");
  return data;
}

export async function likeLore(loreId: number) {
  const { data } = await apiClient.post<MutationMessage>(`/likes/${loreId}`);
  return data;
}

export async function unlikeLore(loreId: number) {
  const { data } = await apiClient.delete<MutationMessage>(`/likes/${loreId}`);
  return data;
}