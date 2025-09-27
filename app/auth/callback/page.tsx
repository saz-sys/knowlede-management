"use client";

import { createClientComponentClient } from "@supabase/auth-helpers-nextjs";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";

export default function AuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/";

  useEffect(() => {
    const handleAuthCallback = async () => {
      const supabase = createClientComponentClient();
      
      try {
        const { data, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error("Auth callback error:", error);
          router.push("/login?error=auth_failed");
          return;
        }

        if (data.session) {
          // ログイン成功
          router.push(redirectTo);
        } else {
          // セッションが見つからない
          router.push("/login?error=no_session");
        }
      } catch (error) {
        console.error("Unexpected error:", error);
        router.push("/login?error=unexpected");
      }
    };

    handleAuthCallback();
  }, [router, redirectTo]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-bold">認証中...</h1>
      <p className="text-slate-600">ログインを処理しています。しばらくお待ちください。</p>
    </main>
  );
}
