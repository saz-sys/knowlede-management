import Link from "next/link";
import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import type { Post } from "@/lib/types/posts";

export default async function PostsPage() {
  const supabase = createServerComponentClient({ cookies });
  const {
    data: { session },
    error
  } = await supabase.auth.getSession();

  if (error || !session) {
    redirect("/login?redirect=/posts");
  }

  const { data: posts, error: fetchError } = await supabase
    .from("posts")
    .select(
      `
        id,
        title,
        summary,
        content,
        url,
        created_at,
        author_email
      `
    )
    .order("created_at", { ascending: false });

  if (fetchError) {
    throw new Error("投稿の取得に失敗しました");
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">投稿一覧</h1>
          <p className="mt-1 text-sm text-gray-600">
            PdEメンバーが共有した最新の知見をチェックしましょう。
          </p>
        </div>
        <Link
          href="/posts/new"
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700"
        >
          新規投稿
        </Link>
      </div>

      <div className="space-y-4">
        {posts?.length ? (
          posts.map((post: Post) => (
            <article
              key={post.id}
              className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition hover:shadow-md"
            >
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>投稿者: {post.author_email ?? "不明"}</span>
                <span>{new Date(post.created_at).toLocaleString("ja-JP")}</span>
              </div>

              <h2 className="mt-2 text-xl font-semibold text-gray-900">
                <Link href={`/posts/${post.id}`} className="hover:underline">
                  {post.title}
                </Link>
              </h2>

              {post.summary && (
                <p className="mt-2 text-sm text-gray-700 line-clamp-3">{post.summary}</p>
              )}

              {!post.summary && post.content && (
                <p className="mt-2 text-sm text-gray-700 line-clamp-3">{post.content}</p>
              )}

              <div className="mt-4 flex items-center justify-between text-sm">
                {post.url && (
                  <a
                    href={post.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    記事を開く →
                  </a>
                )}
                <Link
                  href={`/posts/${post.id}`}
                  className="text-blue-600 hover:text-blue-800"
                >
                  詳細を見る
                </Link>
              </div>
            </article>
          ))
        ) : (
          <div className="rounded-md border border-dashed border-gray-300 p-8 text-center text-gray-500">
            まだ投稿がありません。最初の知見を共有しましょう。
          </div>
        )}
      </div>
    </div>
  );
}

