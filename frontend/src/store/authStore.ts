"use client";
import { create } from "zustand";
import { persist, createJSONStorage, type StateStorage } from "zustand/middleware";
import type { User } from "@/types";
import * as authApi from "@/lib/api/auth";

// Robust browser check — Node.js 22+ has globalThis.localStorage
// but it's NOT the browser's Web Storage API.
function isBrowser(): boolean {
  return typeof window !== "undefined" && typeof window.document !== "undefined";
}

// SSR-safe storage for Zustand persist
const safeStorage: StateStorage = {
  getItem: (name: string): string | null => {
    if (!isBrowser()) return null;
    try {
      return window.localStorage.getItem(name);
    } catch {
      return null;
    }
  },
  setItem: (name: string, value: string): void => {
    if (!isBrowser()) return;
    try {
      window.localStorage.setItem(name, value);
    } catch {}
  },
  removeItem: (name: string): void => {
    if (!isBrowser()) return;
    try {
      window.localStorage.removeItem(name);
    } catch {}
  },
};

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string, personality: string) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
  updateUser: (user: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: false,
      isAuthenticated: false,

      login: async (email, password) => {
        set({ isLoading: true });
        // Clear any stale tokens before attempting login so the interceptor
        // doesn't try to refresh them on a 401 wrong-credentials response.
        authApi.logout();
        try {
          const { user } = await authApi.login(email, password);
          set({ user, isAuthenticated: true });
        } finally {
          set({ isLoading: false });
        }
      },

      signup: async (email, password, name, personality) => {
        set({ isLoading: true });
        try {
          const { user } = await authApi.signup(email, password, name, personality);
          set({ user, isAuthenticated: true });
        } finally {
          set({ isLoading: false });
        }
      },

      logout: () => {
        authApi.logout();
        set({ user: null, isAuthenticated: false });
      },

      fetchMe: async () => {
        try {
          const user = await authApi.getMe();
          set({ user, isAuthenticated: true });
        } catch {
          set({ user: null, isAuthenticated: false });
        }
      },

      updateUser: (updates) => {
        const current = get().user;
        if (current) set({ user: { ...current, ...updates } });
      },
    }),
    {
      name: "emora-auth",
      storage: createJSONStorage(() => safeStorage),
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
