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
        // デバッグ用ログ
        console.log("[AuthCallback] Starting authentication callback");
        console.log("[AuthCallback] Current URL:", window.location.href);
        
        // OAuth認証の場合は、URLハッシュから認証情報を処理
        const { data, error } = await supabase.auth.getSession();
        
        console.log("[AuthCallback] Session data:", { data, error });
        
        if (error) {
          console.error("Auth callback error:", error);
          router.push("/login?error=auth_failed");
          return;
        }

        if (data.session) {
          console.log("[AuthCallback] Session found, checking user info");
          
          // セッションが存在する場合、ユーザー情報も確認
          const { data: { user }, error: userError } = await supabase.auth.getUser();
          
          console.log("[AuthCallback] User data:", { user, userError });
          
          if (userError) {
            console.error("User fetch error:", userError);
            router.push("/login?error=auth_failed");
            return;
          }

          if (user) {
            console.log("[AuthCallback] Login successful, redirecting to:", redirectTo);
            // ログイン成功 - 少し待ってからリダイレクト
            setTimeout(() => {
              router.push(redirectTo);
            }, 100);
          } else {
            console.log("[AuthCallback] No user found");
            // ユーザー情報が取得できない
            router.push("/login?error=no_session");
          }
        } else {
          console.log("[AuthCallback] No session found");
          // セッションが見つからない
          router.push("/login?error=no_session");
        }
      } catch (error) {
        console.error("Unexpected error:", error);
        router.push("/login?error=unexpected");
      }
    };

    // 少し遅延させてから認証処理を実行
    const timer = setTimeout(handleAuthCallback, 100);
    return () => clearTimeout(timer);
  }, [router, redirectTo]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-bold">認証中...</h1>
      <p className="text-slate-600">ログインを処理しています。しばらくお待ちください。</p>
    </main>
  );
}
