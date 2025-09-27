import "./globals.css";
import type { Metadata } from "next";
import { ReactNode } from "react";
import SupabaseProvider from "@/components/providers/SupabaseProvider";
import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";

export const metadata: Metadata = {
  title: "Engineering Knowledge Sharing",
  description: "PdEナレッジ共有プラットフォーム"
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  const supabase = createServerComponentClient({ cookies });
  const {
    data: { session }
  } = await supabase.auth.getSession();

  return (
    <html lang="ja">
      <body>
        <SupabaseProvider session={session}>{children}</SupabaseProvider>
      </body>
    </html>
  );
}
