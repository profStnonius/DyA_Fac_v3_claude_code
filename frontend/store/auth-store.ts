import { create } from "zustand";
import { persist, type StateStorage } from "zustand/middleware";

const cookieStorage: StateStorage = {
  getItem: (name) => {
    if (typeof document === "undefined") return null;
    const match = document.cookie.match(new RegExp(`(?:^|; )${encodeURIComponent(name)}=([^;]*)`));
    return match ? decodeURIComponent(match[1]) : null;
  },
  setItem: (name, value) => {
    if (typeof document === "undefined") return;
    const maxAge = 60 * 60 * 24 * 30; // 30 days, matches JWT_REFRESH_TOKEN_EXPIRE_DAYS
    document.cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}; SameSite=Lax`;
  },
  removeItem: (name) => {
    if (typeof document === "undefined") return;
    document.cookie = `${encodeURIComponent(name)}=; path=/; max-age=0`;
  },
};

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  tenantId: string | null;
  role: string | null;
  user: { id: string; email: string; full_name: string | null } | null;
  setAuth: (data: {
    access_token: string;
    refresh_token: string;
    tenant_id: string;
    role: string;
    user: { id: string; email: string; full_name: string | null };
  }) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      tenantId: null,
      role: null,
      user: null,
      setAuth: (data) =>
        set({
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          tenantId: data.tenant_id,
          role: data.role,
          user: data.user,
        }),
      clearAuth: () =>
        set({ accessToken: null, refreshToken: null, tenantId: null, role: null, user: null }),
    }),
    { name: "cfdi-auth", storage: cookieStorage }
  )
);
