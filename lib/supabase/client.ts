import { createBrowserClient } from "@supabase/auth-helpers-nextjs";
import { env } from "@/lib/config/env";

export const createSupabaseClient = () => {
  return createBrowserClient(env.supabaseUrl, env.supabaseAnonKey);
};
