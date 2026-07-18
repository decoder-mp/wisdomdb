import { apiClient } from "@/lib/axios";
import type { User } from "@/types/api";

export async function fetchCurrentUser() {
  const { data } = await apiClient.get<User>("/users/me");
  return data;
}

export async function fetchUserById(userId: number) {
  const { data } = await apiClient.get<User>(`/users/${userId}`);
  return data;
}

export async function fetchUsers() {
  const { data } = await apiClient.get<User[]>("/users/");
  return data;
}