"use client";

import Link from "next/link";
import { useSessionContext } from "@supabase/auth-helpers-react";
import LogoutButton from "@/components/LogoutButton";

export default function Header() {
  const { session, isLoading } = useSessionContext();

  return (
    <header className="border-b border-slate-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-4">
          <Link href="/" className="text-lg font-semibold text-slate-900 hover:text-brand">
            PdE Knowledge Hub
          </Link>
          {session && (
            <nav className="hidden gap-3 text-sm font-medium text-slate-600 sm:flex">
              <Link href="/posts" className="hover:text-brand-dark">
                投稿一覧
              </Link>
              <Link href="/posts/new" className="hover:text-brand-dark">
                新規投稿
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
            <Link
              href="/login"
              className="rounded-md bg-brand px-3 py-2 font-semibold text-white hover:bg-brand-dark"
            >
              ログイン
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}

