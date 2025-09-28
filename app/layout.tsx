import "./globals.css";
import type { Metadata } from "next";
import { ReactNode } from "react";
import SupabaseProvider from "@/components/providers/SupabaseProvider";
import Header from "@/components/Header";
import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";

export const metadata: Metadata = {
  title: "Engineering Knowledge Sharing",
  description: "PdEナレッジ共有プラットフォーム",
  icons: {
    icon: [
      { url: "/favicon.ico" },
      { url: "/branding/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/branding/favicon-32x32.png", sizes: "32x32", type: "image/png" }
    ],
    shortcut: "/favicon.ico",
    apple: "/branding/apple-touch-icon.png"
  },
  manifest: "/site.webmanifest"
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  const supabase = createServerComponentClient({ cookies });
  const {
    data: { session }
  } = await supabase.auth.getSession();

  return (
    <html lang="ja">
      <body className="bg-slate-50 text-slate-900">
        <SupabaseProvider session={session}>
          <Header />
          <main className="min-h-screen">
            {children}
          </main>
        </SupabaseProvider>
      </body>
    </html>
  );
}
