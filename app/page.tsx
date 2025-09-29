"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useSessionContext } from "@supabase/auth-helpers-react";
import type { Post } from "@/lib/types/posts";
import BookmarkButton from "@/components/bookmarks/BookmarkButton";
import PostSearch from "@/components/posts/PostSearch";

type SourceFilter = "all" | "manual" | "rss";

interface PostWithTags extends Post {
  post_tags?: { tag: { id: string; name: string } }[];
  comments?: { count: number }[];
  bookmarks?: { count: number }[];
}

async function fetchPosts(params: { source?: SourceFilter; tag?: string } = {}) {
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

function createExcerpt(text: string, maxLength = 200) {
  const normalized = text.replace(/\r\n/g, "\n").trim();
  if (normalized.length <= maxLength) {
    return normalized;
  }

  const slice = normalized.slice(0, maxLength);
  const lastBreak = slice.lastIndexOf("\n");
  const lastSpace = slice.lastIndexOf(" ");
  const cutIndex = Math.max(lastBreak, lastSpace);
  const truncated = cutIndex > maxLength * 0.5 ? slice.slice(0, cutIndex) : slice;

  return `${truncated.trimEnd()}…`;
}

export default function HomePage() {
  const { session, isLoading: isSessionLoading } = useSessionContext();
  const [posts, setPosts] = useState<PostWithTags[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [source, setSource] = useState<SourceFilter>("all");
  const [tag, setTag] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<PostWithTags[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [bookmarkedPostIds, setBookmarkedPostIds] = useState<Set<string>>(new Set());
  const hasLoadedOnceRef = useRef(false);

  useEffect(() => {
    if (!isSessionLoading && !session) {
      window.location.href = "/login?redirect=/";
    }
  }, [isSessionLoading, session]);

  const loadBookmarks = async () => {
    try {
      const response = await fetch("/api/bookmarks/my");
      if (response.ok) {
        const { bookmarkedPostIds } = await response.json();
        setBookmarkedPostIds(new Set(bookmarkedPostIds));
      }
    } catch (err) {
      console.error("Failed to load bookmarks:", err);
    }
  };

  const loadPosts = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchPosts();
      setPosts(data);
      // ブックマーク一覧も同時に取得
      await loadBookmarks();
    } catch (err) {
      setError(err instanceof Error ? err.message : "投稿の取得に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    
    if (!query.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    try {
      setIsSearching(true);
      const params = new URLSearchParams({
        q: query,
        limit: "50"
      });

      if (source !== "all") {
        params.append("source", source);
      }
      if (tag) {
        params.append("tag", tag);
      }

      const response = await fetch(`/api/posts/search?${params}`);
      
      if (!response.ok) {
        throw new Error("検索に失敗しました");
      }

      const data = await response.json();
      setSearchResults(data.posts || []);
    } catch (err) {
      console.error("Search failed:", err);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleRefreshRss = async () => {
    try {
      setIsLoading(true);
      const response = await fetch("/api/rss/refresh", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        }
        // feed_idを指定しないことで、すべてのアクティブなフィードを更新
      });
      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.error ?? "RSSの更新に失敗しました");
      }
      await loadPosts();
    } catch (err) {
      alert(err instanceof Error ? err.message : "RSSの更新に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (session && !hasLoadedOnceRef.current) {
      hasLoadedOnceRef.current = true;
      loadPosts();
    }
  }, [session]);

  const availableTags = useMemo(() => deriveTags(posts), [posts]);

  const displayPosts = useMemo(() => {
    // 検索中は検索結果を表示
    if (searchQuery.trim()) {
      return searchResults;
    }
    
    // 通常のフィルタリング
    return posts.filter((post) => {
      const isRss = post.metadata?.source === "rss";
      const matchesSource =
        source === "all" ? true : source === "manual" ? !isRss : isRss;
      const matchesTag = tag
        ? post.post_tags?.some((item) => item.tag.name === tag) ?? false
        : true;
      return matchesSource && matchesTag;
    });
  }, [posts, source, tag, searchQuery, searchResults]);

  if (isSessionLoading || !session) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 text-sm text-gray-600">
        読み込み中です…
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <main className="mx-auto max-w-4xl px-4 py-8 space-y-6">
        <div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h1 className="text-3xl font-bold ocean-text">🌊 Tech Reef</h1>
            <p className="mt-1 text-sm text-slate-700">エンジニアの知識共有プラットフォーム</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleRefreshRss}
              className="ocean-button"
            >
              RSSを更新
            </button>
            <Link
              href="/posts/new"
              className="coral-button"
            >
              新規投稿
            </Link>
          </div>
        </div>

        <section className="rounded-lg border bg-white p-4 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">検索・フィルタ</h2>
          
          {/* 検索フォーム */}
          <div className="mt-4">
            <PostSearch
              onSearch={handleSearch}
              placeholder="投稿を検索..."
              className="mb-0"
            />
          </div>
          
          <div className="mt-4 flex flex-wrap gap-3 text-sm">
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

        {isLoading || isSearching ? (
          <section className="rounded-lg border bg-white p-8 text-center text-sm text-gray-600 shadow-sm">
            {isSearching ? "検索中です…" : "読み込み中です…"}
          </section>
        ) : error ? (
          <section className="rounded-lg border bg-white p-8 text-center text-sm text-red-600 shadow-sm">
            {error}
          </section>
        ) : displayPosts.length === 0 ? (
          <section className="rounded-lg border border-dashed bg-white p-8 text-center text-gray-500 shadow-sm">
            {searchQuery.trim() ? "検索結果が見つかりませんでした。" : "該当する投稿はありません。"}
          </section>
        ) : (
          <div className="space-y-4">
            {displayPosts.map((post) => (
              <article key={post.id} className="ocean-card p-5">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>投稿者: {post.author_email ?? "不明"}</span>
                  <span>{new Date(post.created_at).toLocaleString("ja-JP")}</span>
                </div>

                <h3 className="mt-2 text-xl font-semibold text-gray-900">
                  <Link href={`/posts/${post.id}`} className="hover:underline">
                    {post.title}
                  </Link>
                </h3>

                {post.summary ? (
                  <p className="mt-2 text-sm text-gray-700 whitespace-pre-line">{createExcerpt(post.summary)}</p>
                ) : post.content ? (
                  <p className="mt-2 text-sm text-gray-700 whitespace-pre-line">{createExcerpt(post.content)}</p>
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
                  <div className="flex items-center gap-2">
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
                  <div className="flex items-center gap-3">
                    {/* コメント数とブックマーク数を表示 */}
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        {post.comments?.[0]?.count || 0}
                      </span>
                      <span className="flex items-center gap-1">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                        </svg>
                        {post.bookmarks?.[0]?.count || 0}
                      </span>
                    </div>
                    <BookmarkButton 
                      postId={post.id} 
                      isBookmarked={bookmarkedPostIds.has(post.id)}
                      skipInitialCheck={true}
                      onToggle={(isBookmarked) => {
                        const newBookmarkedIds = new Set(bookmarkedPostIds);
                        if (isBookmarked) {
                          newBookmarkedIds.add(post.id);
                        } else {
                          newBookmarkedIds.delete(post.id);
                        }
                        setBookmarkedPostIds(newBookmarkedIds);
                      }}
                    />
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
