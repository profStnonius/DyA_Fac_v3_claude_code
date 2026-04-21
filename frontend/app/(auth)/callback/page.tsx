"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/store/auth-store";
import { apiClient } from "@/lib/api-client";

export default function OAuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const setAuth = useAuthStore((s) => s.setAuth);

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state");
    const error = searchParams.get("error");

    if (error || !code || !state) {
      router.replace("/login?error=oauth_failed");
      return;
    }

    apiClient
      .post("/api/v1/auth/callback", {
        code,
        redirect_uri: `${window.location.origin}/callback`,
        state,
      })
      .then((res) => {
        setAuth(res.data);
        router.replace("/dashboard");
      })
      .catch(() => {
        router.replace("/login?error=auth_failed");
      });
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600 mx-auto" />
        <p className="mt-4 text-gray-600">Autenticando...</p>
      </div>
    </div>
  );
}
