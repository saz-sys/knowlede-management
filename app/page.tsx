"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useSessionContext } from "@supabase/auth-helpers-react";
import type { Post } from "@/lib/types/posts";
import BookmarkButton from "@/components/bookmarks/BookmarkButton";
import LikeButton from "@/components/posts/LikeButton";
import PostSearch from "@/components/posts/PostSearch";
import { useInfiniteScroll } from "@/hooks/useInfiniteScroll";
import { Metadata } from "next";

type SourceFilter = "all" | "manual" | "rss";

interface PostWithTags extends Post {
  post_tags?: { tag: { id: string; name: string } }[];
  comments?: { count: number }[];
  bookmarks?: { count: number }[];
  post_likes?: { count: number }[];
}

async function fetchPosts(params: { 
  source?: SourceFilter; 
  tag?: string; 
  page?: number; 
  limit?: number;
} = {}) {
  const query = new URLSearchParams();
  if (params.source && params.source !== "all") {
    query.set("source", params.source);
  }
  if (params.tag) {
    query.set("tag", params.tag);
  }
  if (params.page) {
    query.set("page", params.page.toString());
  }
  if (params.limit) {
    query.set("limit", params.limit.toString());
  }

  const response = await fetch(`/api/posts?${query.toString()}`);
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(data?.error ?? "投稿の取得に失敗しました");
  }
  const { posts, pagination } = await response.json();
  return { posts: posts as PostWithTags[], pagination };
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
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [source, setSource] = useState<SourceFilter>("all");
  const [tag, setTag] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<PostWithTags[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [bookmarkedPostIds, setBookmarkedPostIds] = useState<Set<string>>(new Set());
  const [likedPostIds, setLikedPostIds] = useState<Set<string>>(new Set());
  const [availableTags, setAvailableTags] = useState<string[]>([]);
  const [isFilterExpanded, setIsFilterExpanded] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    hasMore: true,
    total: 0
  });
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

  const loadLikes = async () => {
    try {
      const response = await fetch("/api/posts/my-likes");
      if (response.ok) {
        const { likedPostIds } = await response.json();
        setLikedPostIds(new Set(likedPostIds));
      }
    } catch (err) {
      console.error("Failed to load likes:", err);
    }
  };

  const fetchAvailableTags = async () => {
    try {
      const response = await fetch("/api/tags");
      if (response.ok) {
        const tags = await response.json();
        setAvailableTags(tags);
      }
    } catch (err) {
      console.error("Failed to load tags:", err);
    }
  };

  const loadPosts = async (reset = true) => {
    if (reset) {
      setIsLoading(true);
      setError(null);
    } else {
      setIsLoadingMore(true);
    }
    
    try {
      const { posts: newPosts, pagination: newPagination } = await fetchPosts({
        source,
        tag: tag || undefined,
        page: reset ? 1 : pagination.page + 1,
        limit: 10
      });
      
      if (reset) {
        setPosts(newPosts);
        setPagination({
          page: 1,
          hasMore: newPagination.hasMore,
          total: newPagination.total
        });
        // ブックマーク一覧といいね一覧、タグ一覧も同時に取得
        await Promise.all([loadBookmarks(), loadLikes(), fetchAvailableTags()]);
        setIsInitialLoad(false);
      } else {
        setPosts(prev => [...prev, ...newPosts]);
        setPagination(prev => ({
          ...prev,
          page: newPagination.page,
          hasMore: newPagination.hasMore,
          total: newPagination.total
        }));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "投稿の取得に失敗しました");
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  };

  const loadMorePosts = () => {
    if (!pagination.hasMore || isLoadingMore || isSearching) return;
    loadPosts(false);
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
      loadPosts(true);
    }
  }, [session]);

  // フィルタ変更時に投稿を再読み込み
  useEffect(() => {
    if (session && hasLoadedOnceRef.current) {
      loadPosts(true);
    }
  }, [source, tag]);

  // availableTagsはAPIから取得するため、useMemoは不要

  const displayPosts = useMemo(() => {
    // 検索中は検索結果を表示
    if (searchQuery.trim()) {
      return searchResults;
    }
    
    // 通常のフィルタリング（APIでフィルタリング済みなのでそのまま返す）
    return posts;
  }, [posts, searchQuery, searchResults]);

  // 無限スクロールの設定
  const { loadMoreRef } = useInfiniteScroll({
    hasMore: pagination.hasMore && !isSearching,
    isLoading: isLoadingMore,
    onLoadMore: loadMorePosts,
  });

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

        <section className="rounded-lg border bg-white shadow-sm">
          <button
            onClick={() => setIsFilterExpanded(!isFilterExpanded)}
            className="w-full p-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <h2 className="text-lg font-semibold text-gray-900">検索・フィルタ</h2>
            <svg
              className={`w-5 h-5 text-gray-500 transition-transform ${isFilterExpanded ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {isFilterExpanded && (
            <div className="px-4 pb-4 border-t border-gray-200">
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
            </div>
          )}
        </section>

        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="ocean-card p-4 animate-pulse">
                <div className="flex items-center justify-between mb-2">
                  <div className="h-3 bg-gray-200 rounded w-32"></div>
                  <div className="h-3 bg-gray-200 rounded w-24"></div>
                </div>
                <div className="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
                <div className="flex items-center justify-between">
                  <div className="flex gap-2">
                    <div className="h-6 bg-gray-200 rounded-full w-16"></div>
                    <div className="h-6 bg-gray-200 rounded-full w-20"></div>
                  </div>
                  <div className="flex gap-2">
                    <div className="h-6 bg-gray-200 rounded w-6"></div>
                    <div className="h-6 bg-gray-200 rounded w-6"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
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
              <article key={post.id} className="ocean-card p-4 hover:shadow-lg transition-shadow">
                <Link href={`/posts/${post.id}`} className="block" prefetch={true}>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>投稿者: {post.author_email ?? "不明"}</span>
                    <span>{new Date(post.created_at).toLocaleString("ja-JP")}</span>
                  </div>

                  <h3 className="mt-1 text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors line-clamp-2">
                    {post.title}
                  </h3>

                  {post.summary ? (
                    <p className="mt-1 text-sm text-gray-600 line-clamp-2">{createExcerpt(post.summary, 120)}</p>
                  ) : post.content ? (
                    <p className="mt-1 text-sm text-gray-600 line-clamp-2">{createExcerpt(post.content, 120)}</p>
                  ) : null}

                  <div className="mt-2 flex items-center justify-between">
                    <div className="flex flex-wrap gap-1 text-xs">
                      {post.metadata?.source === "rss" ? (
                        <span className="rounded-full bg-amber-100 px-2 py-0.5 text-amber-700">RSS</span>
                      ) : (
                        <span className="rounded-full bg-green-100 px-2 py-0.5 text-green-700">ユーザー</span>
                      )}
                      {post.post_tags?.slice(0, 2).map((item) => (
                        <span key={item.tag.id} className="rounded-full bg-blue-100 px-2 py-0.5 text-blue-800">
                          {item.tag.name}
                        </span>
                      ))}
                    </div>
                    
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        {post.comments?.[0]?.count || 0}
                      </span>
                      <span className="flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                        </svg>
                        {post.bookmarks?.[0]?.count || 0}
                      </span>
                      <span className="flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                        </svg>
                        {post.post_likes?.[0]?.count || 0}
                      </span>
                    </div>
                  </div>
                </Link>
                
                {/* ボタンエリアをLinkの外に配置 */}
                <div className="mt-2 flex items-center justify-end gap-1">
                  <LikeButton 
                    postId={post.id}
                    initialLikeCount={post.post_likes?.[0]?.count || 0}
                    initialIsLiked={likedPostIds.has(post.id)}
                    skipInitialCheck={true}
                    onToggle={(isLiked) => {
                      const newLikedIds = new Set(likedPostIds);
                      if (isLiked) {
                        newLikedIds.add(post.id);
                      } else {
                        newLikedIds.delete(post.id);
                      }
                      setLikedPostIds(newLikedIds);
                    }}
                  />
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
              </article>
              ))}
              
            {/* 無限スクロール用のトリガー要素 */}
            <div ref={loadMoreRef} className="flex justify-center py-4">
              {isLoadingMore && (
                <div className="text-sm text-gray-500">読み込み中...</div>
              )}
              {!pagination.hasMore && displayPosts.length > 0 && (
                <div className="text-sm text-gray-500">すべての投稿を読み込みました</div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
