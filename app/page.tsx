import Link from "next/link";
import { getSession } from "@/lib/auth/server";

export default async function Home() {
  const session = await getSession();

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-3xl font-bold text-brand">Engineering Knowledge Sharing</h1>
      {session ? (
        <p className="text-slate-600">ようこそ、{session.user.email}</p>
      ) : (
        <div className="flex flex-col items-center gap-2">
          <p className="text-slate-600">ログインしてサービスを利用しましょう。</p>
          <Link
            href="/login"
            className="rounded bg-brand px-4 py-2 font-semibold text-white hover:bg-brand-dark"
          >
            ログインページへ
          </Link>
        </div>
      )}
    </main>
  );
}
