import "./globals.css";
import type { Metadata } from "next";
import { ReactNode } from "react";
import SupabaseProvider from "@/components/providers/SupabaseProvider";
import Header from "@/components/Header";
import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";

export const metadata: Metadata = {
  title: "Tech Reef",
  description: "エンジニアの知識共有プラットフォーム",
  icons: {
    icon: { url: "/favicon.ico", type: "image/x-icon" },
    shortcut: { url: "/favicon.ico", type: "image/x-icon" },
    apple: { url: "/branding/apple-touch-icon.png", sizes: "180x180" }
  },
  manifest: "/site.webmanifest",
  openGraph: {
    title: "Tech Reef",
    description: "エンジニアの知識共有プラットフォーム",
    images: ["/branding/og-image.png"],
    type: "website",
    siteName: "Tech Reef",
    locale: "ja_JP"
  },
  twitter: {
    card: "summary_large_image",
    title: "Tech Reef",
    description: "エンジニアの知識共有プラットフォーム",
    images: ["/branding/og-image.png"]
  }
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  const supabase = createServerComponentClient({ cookies });
  const {
    data: { session }
  } = await supabase.auth.getSession();

  return (
    <html lang="ja">
      <head>
        <link rel="icon" type="image/x-icon" href="/favicon.ico" />
        <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/branding/apple-touch-icon.png" />
      </head>
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
