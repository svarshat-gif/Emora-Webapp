import { apiClient } from "./client";
import type { User, ApiResponse } from "@/types";

export interface ProfileUpdatePayload {
  name?: string;
  bio?: string;
  personality?: string;
  theme?: string;
  notification_enabled?: boolean;
  avatar_url?: string;
}

export async function getProfile(): Promise<User> {
  const { data } = await apiClient.get<ApiResponse<User>>("/profile");
  return data.data;
}

export async function updateProfile(payload: ProfileUpdatePayload): Promise<User> {
  const { data } = await apiClient.put<ApiResponse<User>>("/profile", payload);
  return data.data;
}

export async function getStreak(): Promise<{ streak: number; total_entries: number }> {
  const { data } = await apiClient.get("/profile/streak");
  return data.data;
}
