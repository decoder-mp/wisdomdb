import { apiClient } from "@/lib/axios";
import type { Lore, MutationMessage, User } from "@/types/api";

export type AdminStats = {
  users: number;
  lore: number;
  comments: number;
  likes: number;
  admins: number;
};

export async function fetchAdminStats() {
  const { data } = await apiClient.get<AdminStats>("/admin/stats");
  return data;
}

export async function fetchAdminUsers() {
  const { data } = await apiClient.get<User[]>("/admin/users");
  return data;
}

export async function fetchAdminLore() {
  const { data } = await apiClient.get<Lore[]>("/admin/lore");
  return data;
}

export async function deleteAdminUser(userId: number) {
  const { data } = await apiClient.delete<{ message: string }>(`/admin/users/${userId}`);
  return data;
}

export async function deleteAdminLore(loreId: number) {
  const { data } = await apiClient.delete<{ message: string }>(`/admin/lore/${loreId}`);
  return data;
}

export async function toggleAdminUser(userId: number) {
  const { data } = await apiClient.patch<{ id: number; username: string; is_admin: boolean }>(
    `/admin/users/${userId}/toggle-admin`,
  );
  return data;
}

export async function resetAdminUserPassword(email: string, newPassword: string) {
  const { data } = await apiClient.post<MutationMessage>("/auth/reset-password", {
    email,
    new_password: newPassword,
  });
  return data;
}
