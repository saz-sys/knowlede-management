"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import type { Post } from "@/lib/types/posts";

type SourceFilter = "all" | "manual" | "rss";

interface PostWithTags extends Post {
  tags?: { tag: { id: string; name: string } }[];
}

async function fetchPosts(params: { source?: SourceFilter; tag?: string }) {
  const query = new URLSearchParams();
  if (params.source && params.source !== "all") {
    query.set("source", params.source);
  }
  if (params.tag) {
    query.set("tag", params.tag);
  }

  const response = await fetch(`/api/posts?${query.toString()}`);
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(data?.error ?? "投稿の取得に失敗しました");
  }
  const { posts } = await response.json();
  return posts as PostWithTags[];
}

function deriveTags(posts: PostWithTags[]) {
  const tags = new Set<string>();
  posts.forEach((post) => post.post_tags?.forEach((item) => tags.add(item.tag.name)));
  return Array.from(tags).sort();
}

export default function PostsPage() {
  const [posts, setPosts] = useState<PostWithTags[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [source, setSource] = useState<SourceFilter>("all");
  const [tag, setTag] = useState<string | null>(null);
  const [availableTags, setAvailableTags] = useState<string[]>([]);

  const loadPosts = async (params: { source?: SourceFilter; tag?: string | null }) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchPosts({ source: params.source, tag: params.tag ?? undefined });
      setPosts(data);
      setAvailableTags(deriveTags(data));
    } catch (err) {
      setError(err instanceof Error ? err.message : "投稿の取得に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPosts({ source, tag });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [source, tag]);

  const displayPosts = useMemo(() => posts, [posts]);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">投稿一覧</h1>
          <p className="mt-1 text-sm text-gray-600">PdEメンバーとRSSから取り込んだ最新の知見をチェックしましょう。</p>
        </div>
        <Link
          href="/posts/new"
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700"
        >
          新規投稿
        </Link>
      </div>

      <section className="rounded-lg border bg-white p-4 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900">フィルタ</h2>
        <div className="mt-3 flex flex-wrap gap-3 text-sm">
          {["all", "manual", "rss"].map((key) => (
            <button
              key={key}
              onClick={() => setSource(key as SourceFilter)}
              className={`rounded-full px-3 py-1 transition ${
                source === key ? "bg-blue-600 text-white shadow" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {key === "all" ? "すべて" : key === "manual" ? "ユーザー投稿" : "RSS投稿"}
            </button>
          ))}
        </div>

        {availableTags.length > 0 && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700">タグ</label>
            <div className="mt-2 flex flex-wrap gap-2">
              <button
                onClick={() => setTag(null)}
                className={`rounded-full px-3 py-1 text-sm ${
                  tag === null ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600"
                }`}
              >
                すべて
              </button>
              {availableTags.map((availableTag) => (
                <button
                  key={availableTag}
                  onClick={() => setTag(availableTag)}
                  className={`rounded-full px-3 py-1 text-sm ${
                    tag === availableTag ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600"
                  }`}
                >
                  {availableTag}
                </button>
              ))}
            </div>
          </div>
        )}
      </section>

      {isLoading ? (
        <section className="rounded-lg border bg-white p-8 text-center text-sm text-gray-600 shadow-sm">
          読み込み中です…
        </section>
      ) : error ? (
        <section className="rounded-lg border bg-white p-8 text-center text-sm text-red-600 shadow-sm">
          {error}
        </section>
      ) : displayPosts.length === 0 ? (
        <section className="rounded-lg border border-dashed bg-white p-8 text-center text-gray-500 shadow-sm">
          該当する投稿はありません。
        </section>
      ) : (
        <div className="space-y-4">
          {displayPosts.map((post) => (
            <article key={post.id} className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition hover:shadow-md">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>投稿者: {post.author_email ?? "不明"}</span>
                <span>{new Date(post.created_at).toLocaleString("ja-JP")}</span>
              </div>

              <h2 className="mt-2 text-xl font-semibold text-gray-900">
                <Link href={`/posts/${post.id}`} className="hover:underline">
                  {post.title}
                </Link>
              </h2>

              {post.summary ? (
                <p className="mt-2 text-sm text-gray-700 line-clamp-3">{post.summary}</p>
              ) : post.content ? (
                <p className="mt-2 text-sm text-gray-700 line-clamp-3">{post.content}</p>
              ) : null}

              <div className="mt-3 flex flex-wrap gap-1 text-xs text-gray-500">
                {post.metadata?.source === "rss" ? (
                  <span className="rounded-full bg-amber-100 px-2 py-0.5 text-amber-700">RSS</span>
                ) : (
                  <span className="rounded-full bg-green-100 px-2 py-0.5 text-green-700">ユーザー</span>
                )}
                {post.post_tags?.map((item) => (
                  <span key={item.tag.id} className="rounded-full bg-blue-100 px-2 py-0.5 text-blue-800">
                    {item.tag.name}
                  </span>
                ))}
              </div>

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
                <Link href={`/posts/${post.id}`} className="text-blue-600 hover:text-blue-800">
                  詳細を見る
                </Link>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

