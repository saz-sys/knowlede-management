"use client";

import { ReactNode, useMemo } from "react";
import { SessionContextProvider } from "@supabase/auth-helpers-react";
import { Session } from "@supabase/supabase-js";
import { createSupabaseClient } from "@/lib/supabase/client";

interface SupabaseProviderProps {
  children: ReactNode;
  session?: Session | null;
}

export default function SupabaseProvider({ children, session }: SupabaseProviderProps) {
  const supabase = useMemo(() => createSupabaseClient(), []);

  return (
    <SessionContextProvider supabaseClient={supabase} initialSession={session}>
      {children}
    </SessionContextProvider>
  );
}
