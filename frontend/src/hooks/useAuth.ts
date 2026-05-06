"use client";
import { useAuthStore } from "@/store/authStore";

export function useAuth() {
  const { user, isAuthenticated, isLoading, login, signup, logout, fetchMe } = useAuthStore();
  return { user, isAuthenticated, isLoading, login, signup, logout, fetchMe };
}
