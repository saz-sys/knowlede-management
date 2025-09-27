import { createBrowserClient } from "@supabase/auth-helpers-nextjs";
import { env } from "@/lib/config/env";

export default function LoginPage() {
  const handleLogin = async () => {
    const supabase = createBrowserClient(env.supabaseUrl, env.supabaseAnonKey);
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        queryParams: {
          access_type: "offline",
          prompt: "consent"
        }
      }
    });
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6">
      <h1 className="text-3xl font-bold">PdE SSO Login</h1>
      <button
        type="button"
        onClick={handleLogin}
        className="rounded bg-brand px-4 py-2 font-semibold text-white hover:bg-brand-dark"
      >
        Sign in with Google
      </button>
    </main>
  );
}
