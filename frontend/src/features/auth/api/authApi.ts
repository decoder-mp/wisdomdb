import { apiClient } from "@/lib/axios";
import type { MutationMessage } from "@/types/api";

type LoginPayload = {
  email: string;
  password: string;
};

type RegisterPayload = {
  username: string;
  email: string;
  password: string;
};

type ForgotPasswordPayload = {
  email: string;
};

type CompletePasswordResetPayload = {
  token: string;
  new_password: string;
};

type ChangePasswordPayload = {
  current_password: string;
  new_password: string;
};

export async function login(payload: LoginPayload) {
  const body = new URLSearchParams();
  body.set("username", payload.email);
  body.set("password", payload.password);
  const { data } = await apiClient.post("/auth/login", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data as { access_token: string; token_type: string };
}

export async function register(payload: RegisterPayload) {
  const { data } = await apiClient.post("/auth/register", payload);
  return data;
}

export async function forgotPassword(payload: ForgotPasswordPayload) {
  const { data } = await apiClient.post<MutationMessage>("/auth/forgot-password", payload);
  return data;
}

export async function completePasswordReset(payload: CompletePasswordResetPayload) {
  const { data } = await apiClient.post<MutationMessage>("/auth/complete-password-reset", payload);
  return data;
}

export async function changePassword(payload: ChangePasswordPayload) {
  const { data } = await apiClient.post<MutationMessage>("/auth/change-password", payload);
  return data;
}
