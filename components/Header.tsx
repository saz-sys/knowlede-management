"use client";

import Link from "next/link";
import { useSessionContext } from "@supabase/auth-helpers-react";
import LogoutButton from "@/components/LogoutButton";
import { createClientComponentClient } from "@supabase/auth-helpers-nextjs";

export default function Header() {
  const { session, isLoading } = useSessionContext();

  const handleLogin = async () => {
    const redirectTo = window.location.pathname + window.location.search;
    const supabase = createClientComponentClient();
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback?redirect=${encodeURIComponent(
          redirectTo
        )}`,
        queryParams: {
          access_type: "offline",
          prompt: "consent"
        }
      }
    });
  };

  return (
    <header className="border-b border-slate-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-4">
          <Link href="/" className="text-lg font-semibold text-slate-900 hover:text-brand">
            PdE Knowledge Hub
          </Link>
          {session && (
            <nav className="hidden gap-3 text-sm font-medium text-slate-600 sm:flex">
              <Link href="/posts/new" className="hover:text-brand-dark">
                新規投稿
              </Link>
              <Link href="/rss-feeds" className="hover:text-brand-dark">
                RSSフィード
              </Link>
            </nav>
          )}
        </div>

        <div className="flex items-center gap-3 text-sm text-slate-600">
          {isLoading ? (
            <span>読み込み中...</span>
          ) : session ? (
            <>
              <span className="hidden sm:inline">{session.user.email}</span>
              <LogoutButton />
            </>
          ) : (
            <button
              onClick={handleLogin}
              className="rounded-md bg-brand px-3 py-2 font-semibold text-white hover:bg-brand-dark"
            >
              ログイン
            </button>
          )}
        </div>
      </div>
    </header>
  );
}

