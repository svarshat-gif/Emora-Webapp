import { apiClient, setTokens, clearTokens } from "./client";
import type { User, ApiResponse } from "@/types";

export interface AuthData {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export async function signup(email: string, password: string, name: string, personality: string): Promise<AuthData> {
  const { data } = await apiClient.post<ApiResponse<AuthData>>("/auth/signup", { email, password, name, personality });
  setTokens(data.data.access_token, data.data.refresh_token);
  return data.data;
}

export async function login(email: string, password: string): Promise<AuthData> {
  const { data } = await apiClient.post<ApiResponse<AuthData>>("/auth/login", { email, password });
  setTokens(data.data.access_token, data.data.refresh_token);
  return data.data;
}

export async function getMe(): Promise<User> {
  const { data } = await apiClient.get<ApiResponse<User>>("/auth/me");
  return data.data;
}

export async function updateProfile(updates: Partial<Pick<User, "name" | "personality" | "bio">>): Promise<User> {
  const { data } = await apiClient.put<ApiResponse<User>>("/profile", updates);
  return data.data;
}

export function logout() {
  clearTokens();
}
