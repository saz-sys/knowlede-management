import { cookies } from "next/headers";
import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";

export const createSupabaseServerClient = () => {
  return createServerComponentClient({ cookies });
};

export const getSession = async () => {
  const supabase = createSupabaseServerClient();
  const {
    data: { session }
  } = await supabase.auth.getSession();
  return session;
};
