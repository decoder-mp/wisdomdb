import { apiClient } from "@/lib/axios";
import type { Bookmark, MutationMessage } from "@/types/api";

export async function fetchBookmarks() {
  const { data } = await apiClient.get<Bookmark[]>("/bookmarks/me");
  return data;
}

export async function createBookmark(loreId: number) {
  const { data } = await apiClient.post<Bookmark>(`/bookmarks/${loreId}`);
  return data;
}

export async function deleteBookmark(loreId: number) {
  const { data } = await apiClient.delete<MutationMessage>(`/bookmarks/${loreId}`);
  return data;
}