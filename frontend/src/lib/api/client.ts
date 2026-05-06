import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Robust browser check — Node.js 22+ has a globalThis.localStorage
// but it's NOT the same as the browser's Web Storage API.
function isBrowser(): boolean {
  return typeof window !== "undefined" && typeof window.document !== "undefined";
}

function safeGetItem(key: string): string | null {
  if (!isBrowser()) return null;
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

function safeSetItem(key: string, value: string): void {
  if (!isBrowser()) return;
  try {
    window.localStorage.setItem(key, value);
  } catch {}
}

function safeRemoveItem(key: string): void {
  if (!isBrowser()) return;
  try {
    window.localStorage.removeItem(key);
  } catch {}
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// Attach token from localStorage on every request
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = safeGetItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-refresh on 401 — but never retry auth endpoints themselves
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    const url = original?.url ?? "";

    // Skip refresh for auth endpoints — a 401 there means wrong credentials
    const isAuthEndpoint = url.includes("/auth/login") || url.includes("/auth/signup") || url.includes("/auth/refresh");

    if (error.response?.status === 401 && !original._retry && !isAuthEndpoint && isBrowser()) {
      original._retry = true;
      try {
        const refreshToken = safeGetItem("refresh_token");
        if (!refreshToken) throw new Error("No refresh token");

        const { data } = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refreshToken });
        const { access_token, refresh_token } = data.data;

        safeSetItem("access_token", access_token);
        safeSetItem("refresh_token", refresh_token);
        original.headers!.Authorization = `Bearer ${access_token}`;

        return apiClient(original);
      } catch {
        safeRemoveItem("access_token");
        safeRemoveItem("refresh_token");
        if (isBrowser()) window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export function setTokens(access: string, refresh: string) {
  safeSetItem("access_token", access);
  safeSetItem("refresh_token", refresh);
  if (isBrowser()) {
    document.cookie = `access_token=${access}; path=/; max-age=${60 * 30}; SameSite=Lax`;
    document.cookie = `refresh_token=${refresh}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
  }
}

export function clearTokens() {
  safeRemoveItem("access_token");
  safeRemoveItem("refresh_token");
  if (isBrowser()) {
    document.cookie = "access_token=; path=/; max-age=0";
    document.cookie = "refresh_token=; path=/; max-age=0";
  }
}
