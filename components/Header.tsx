"use client";

import Link from "next/link";
import Image from "next/image";
import { useSessionContext } from "@supabase/auth-helpers-react";
import LogoutButton from "@/components/LogoutButton";
import { createClientComponentClient } from "@supabase/auth-helpers-nextjs";
import { useState } from "react";

export default function Header() {
  const { session, isLoading } = useSessionContext();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

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
    <header className="border-b border-gray-200 bg-white shadow-lg">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-4">
          <Link href="/" className="flex items-center hover:opacity-80 transition-opacity">
            <Image 
              src="/branding/logo.png?v=20250129" 
              alt="Tech Reef" 
              width={200}
              height={64}
              style={{ objectFit: 'contain' }}
            />
          </Link>
        </div>

        <div className="flex items-center gap-3 text-sm text-gray-700">
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
              className="coral-button"
            >
              ログイン
            </button>
          )}
          
          {/* ハンバーガーメニューボタン */}
          {session && (
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-md hover:bg-gray-100 text-gray-700"
              aria-label="メニューを開く"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {isMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* ハンバーガーメニュー */}
      {session && isMenuOpen && (
        <div className="border-t border-gray-200 bg-white">
          <nav className="px-4 py-3 space-y-2">
            <Link
              href="/posts/new"
              className="block px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              新規投稿
            </Link>
            <Link
              href="/rss-feeds"
              className="block px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              RSSフィード
            </Link>
            <Link
              href="/resources"
              className="block px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              プロフィール
            </Link>
            <Link
              href="/bookmarks"
              className="block px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              ブックマーク
            </Link>
            <Link
              href="/my-posts"
              className="block px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              マイページ
            </Link>
            
            <Link
              href="/rankings"
              className="block px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              ランキング
            </Link>
            
            <div className="border-t border-gray-200 pt-2 mt-2">
              <div className="px-3 py-2 text-sm text-gray-500">
                {session.user.email}
              </div>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}

