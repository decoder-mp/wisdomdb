import { apiClient } from "@/lib/axios";
import type { Comment, MutationMessage } from "@/types/api";

export async function fetchComments(loreId: number) {
  const { data } = await apiClient.get<Comment[]>(`/comments/${loreId}`);
  return data;
}

export async function createComment(loreId: number, content: string) {
  const { data } = await apiClient.post<Comment>(`/comments/${loreId}`, { content });
  return data;
}

export async function updateComment(commentId: number, content: string) {
  const { data } = await apiClient.patch<Comment>(`/comments/${commentId}`, { content });
  return data;
}

export async function deleteComment(commentId: number) {
  const { data } = await apiClient.delete<MutationMessage>(`/comments/${commentId}`);
  return data;
}