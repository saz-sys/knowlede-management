"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import PostSearch from "./PostSearch";

interface Post {
  id: string;
  title: string;
  url: string;
  summary: string | null;
  author_email: string;
  created_at: string;
  post_tags: Array<{
    tag: {
      id: string;
      name: string;
    };
  }>;
}

interface PostSearchResultsProps {
  initialQuery: string;
  initialTag?: string;
  initialSource?: string;
}

export default function PostSearchResults({ 
  initialQuery, 
  initialTag, 
  initialSource 
}: PostSearchResultsProps) {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState(initialQuery);
  const [tag, setTag] = useState(initialTag || "");
  const [source, setSource] = useState(initialSource || "");
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasSearched, setHasSearched] = useState(!!initialQuery);

  const ITEMS_PER_PAGE = 10;

  useEffect(() => {
    if (initialQuery) {
      performSearch(initialQuery, 1);
    }
  }, [initialQuery]);

  const performSearch = async (searchQuery: string, page: number = 1) => {
    if (!searchQuery.trim()) {
      setPosts([]);
      setTotal(0);
      setHasSearched(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        q: searchQuery,
        limit: ITEMS_PER_PAGE.toString(),
        offset: ((page - 1) * ITEMS_PER_PAGE).toString()
      });

      if (tag) params.append("tag", tag);
      if (source) params.append("source", source);

      const response = await fetch(`/api/posts/search?${params}`);
      
      if (!response.ok) {
        throw new Error("検索に失敗しました");
      }

      const data = await response.json();
      setPosts(data.posts || []);
      setTotal(data.total || 0);
      setCurrentPage(page);
      setHasSearched(true);
    } catch (error) {
      console.error("Search failed:", error);
      setError(error instanceof Error ? error.message : "検索に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (searchQuery: string) => {
    setQuery(searchQuery);
    performSearch(searchQuery, 1);
  };

  const handlePageChange = (page: number) => {
    performSearch(query, page);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("ja-JP", {
      year: "numeric",
      month: "long",
      day: "numeric"
    });
  };

  const totalPages = Math.ceil(total / ITEMS_PER_PAGE);

  return (
    <div className="p-6">
      {/* 検索フォーム */}
      <div className="mb-6">
        <PostSearch
          onSearch={handleSearch}
          placeholder="タイトル、内容、要約で検索..."
          className="mb-4"
        />
        
        {/* フィルター */}
        <div className="flex gap-4 items-center">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              タグ
            </label>
            <input
              type="text"
              value={tag}
              onChange={(e) => setTag(e.target.value)}
              placeholder="タグ名"
              className="px-3 py-1 border border-gray-300 rounded-md text-sm"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              ソース
            </label>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm"
            >
              <option value="">すべて</option>
              <option value="manual">手動投稿</option>
              <option value="rss">RSS</option>
            </select>
          </div>
          
          <button
            onClick={() => performSearch(query, 1)}
            className="mt-6 px-4 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
          >
            フィルター適用
          </button>
        </div>
      </div>

      {/* 検索結果 */}
      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-sm text-gray-600">検索中...</p>
        </div>
      )}

      {error && (
        <div className="text-center py-8">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => performSearch(query, currentPage)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            再試行
          </button>
        </div>
      )}

      {!loading && !error && hasSearched && (
        <>
          {/* 検索結果ヘッダー */}
          <div className="mb-4">
            <p className="text-sm text-gray-600">
              「{query}」の検索結果: {total}件
            </p>
          </div>

          {/* 投稿一覧 */}
          {posts.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-400 mb-4">
                <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p className="text-gray-600">検索結果が見つかりませんでした</p>
            </div>
          ) : (
            <div className="space-y-4">
              {posts.map((post) => (
                <div key={post.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        <Link 
                          href={`/posts/${post.id}`}
                          className="hover:text-blue-600 transition-colors"
                        >
                          {post.title}
                        </Link>
                      </h3>
                      
                      {post.summary && (
                        <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                          {post.summary}
                        </p>
                      )}
                      
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>投稿者: {post.author_email}</span>
                        <span>投稿日: {formatDate(post.created_at)}</span>
                      </div>
                      
                      {post.post_tags && post.post_tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {post.post_tags.map((postTag) => (
                            <span
                              key={postTag.tag.id}
                              className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                            >
                              {postTag.tag.name}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* ページネーション */}
          {totalPages > 1 && (
            <div className="mt-6 flex justify-center">
              <nav className="flex items-center space-x-2">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  前へ
                </button>
                
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                  <button
                    key={page}
                    onClick={() => handlePageChange(page)}
                    className={`px-3 py-1 text-sm border rounded-md ${
                      page === currentPage
                        ? "bg-blue-600 text-white border-blue-600"
                        : "border-gray-300 hover:bg-gray-50"
                    }`}
                  >
                    {page}
                  </button>
                ))}
                
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  次へ
                </button>
              </nav>
            </div>
          )}
        </>
      )}

      {!hasSearched && !loading && (
        <div className="text-center py-8">
          <div className="text-gray-400 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <p className="text-gray-600">キーワードを入力して検索してください</p>
        </div>
      )}
    </div>
  );
}
