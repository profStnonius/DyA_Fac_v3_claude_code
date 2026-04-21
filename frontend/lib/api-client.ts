import axios, { type InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/store/auth-store";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refreshToken = useAuthStore.getState().refreshToken;
      if (refreshToken) {
        try {
          const res = await axios.post(
            `${API_BASE_URL}/api/v1/auth/refresh`,
            { refresh_token: refreshToken },
            { withCredentials: true }
          );
          useAuthStore.getState().setAuth(res.data);
          original.headers.Authorization = `Bearer ${res.data.access_token}`;
          return apiClient(original);
        } catch {
          useAuthStore.getState().clearAuth();
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);
