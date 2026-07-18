import { apiClient } from "@/lib/axios";
import type { ApiList, Notification } from "@/types/api";

export async function fetchNotifications() {
  const { data } = await apiClient.get<ApiList<Notification>>("/notifications");
  return data;
}

export async function fetchUnreadNotifications() {
  const { data } = await apiClient.get<ApiList<Notification>>("/notifications/unread");
  return data;
}

export async function readNotification(id: number) {
  const { data } = await apiClient.patch<Notification>(`/notifications/${id}/read`);
  return data;
}

export async function readAllNotifications() {
  const { data } = await apiClient.patch<{ updated: number }>("/notifications/read-all");
  return data;
}

export async function deleteNotification(id: number) {
  const { data } = await apiClient.delete<{ message: string }>(`/notifications/${id}`);
  return data;
}
