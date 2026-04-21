"use client";

import { useAuthStore } from "@/store/auth-store";

export function Topbar() {
  const user = useAuthStore((s) => s.user);
  const clearAuth = useAuthStore((s) => s.clearAuth);

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-end px-6 gap-4">
      {user && (
        <span className="text-sm text-gray-700">{user.full_name ?? user.email}</span>
      )}
      <button
        onClick={clearAuth}
        className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
      >
        Salir
      </button>
    </header>
  );
}
