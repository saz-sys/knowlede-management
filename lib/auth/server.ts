import { headers, cookies } from "next/headers";
import { createServerClient } from "@supabase/auth-helpers-nextjs";
import { env } from "@/lib/config/env";

export const createSupabaseServerClient = () => {
  const cookieStore = cookies();
  return createServerClient(env.supabaseUrl, env.supabaseAnonKey, {
    cookies: {
      get(name: string) {
        return cookieStore.get(name)?.value;
      },
      set(name: string, value: string, options: any) {
        cookieStore.set({ name, value, ...options });
      },
      remove(name: string, options: any) {
        cookieStore.set({ name, value: "", ...options, maxAge: -1 });
      }
    }
  });
};

export const getSession = async () => {
  const supabase = createSupabaseServerClient();
  const {
    data: { session }
  } = await supabase.auth.getSession();
  return session;
};
