"use client";

import { createClientComponentClient } from "@supabase/auth-helpers-nextjs";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/";

  const handleLogin = async () => {
    const supabase = createClientComponentClient();
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback?redirect=${encodeURIComponent(redirectTo)}`,
        queryParams: {
          access_type: "offline",
          prompt: "consent"
        }
      }
    });
  };

  // 既にログイン済みの場合はリダイレクト
  useEffect(() => {
    const checkSession = async () => {
      const supabase = createClientComponentClient();
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        router.push(redirectTo);
      }
    };
    checkSession();
  }, [router, redirectTo]);

  const error = searchParams.get("error");

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6">
      <h1 className="text-3xl font-bold">PdE SSO Login</h1>
      
      {error && (
        <div className="rounded bg-red-100 border border-red-400 text-red-700 px-4 py-3">
          {error === "auth_failed" && "認証に失敗しました。もう一度お試しください。"}
          {error === "no_session" && "セッションが見つかりません。もう一度ログインしてください。"}
          {error === "unexpected" && "予期しないエラーが発生しました。"}
        </div>
      )}
      
      <button
        type="button"
        onClick={handleLogin}
        className="rounded bg-brand px-4 py-2 font-semibold text-white hover:bg-brand-dark"
      >
        Sign in with Google
      </button>
    </main>
  );
}
