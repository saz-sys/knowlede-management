import Link from "next/link";
import { getSession } from "@/lib/auth/server";
import LogoutButton from "@/components/LogoutButton";

export default async function Home() {
  const session = await getSession();

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-3xl font-bold text-brand">Engineering Knowledge Sharing</h1>
      {session ? (
        <div className="flex flex-col items-center gap-4">
          <p className="text-slate-600">ようこそ、{session.user.email}</p>
          <div className="flex gap-2">
            <Link
              href="/posts"
              className="rounded bg-brand px-4 py-2 font-semibold text-white hover:bg-brand-dark"
            >
              投稿一覧
            </Link>
            <Link
              href="/posts/new"
              className="rounded bg-green-600 px-4 py-2 font-semibold text-white hover:bg-green-700"
            >
              新規投稿
            </Link>
          </div>
          <LogoutButton />
        </div>
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
