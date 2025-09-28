"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface Post {
  id: string;
  title: string;
  url: string;
  summary: string | null;
  created_at: string;
  updated_at: string;
  post_tags: Array<{
    tag: {
      id: string;
      name: string;
    };
  }>;
  _count?: {
    comments: number;
    bookmarks: number;
  };
}

export default function MyPostsList() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    loadPosts();
  }, []);

  const loadPosts = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/posts/my");
      if (!response.ok) {
        throw new Error("投稿の取得に失敗しました");
      }
      const data = await response.json();
      setPosts(data.posts || []);
    } catch (error) {
      console.error("Failed to load posts:", error);
      setError(error instanceof Error ? error.message : "投稿の取得に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (postId: string) => {
    try {
      setDeletingId(postId);
      const response = await fetch(`/api/posts/${postId}`, {
        method: "DELETE"
      });

      if (!response.ok) {
        const data = await response.json();
        
        // 関連データがある場合の特別な処理
        if (data.error === "HAS_RELATED_DATA") {
          const { comments, bookmarks } = data.details;
          const message = `この投稿には関連するデータがあります：\n・コメント: ${comments}件\n・ブックマーク: ${bookmarks}件\n\n削除を続行しますか？関連データもすべて削除されます。`;
          
          if (!confirm(message)) {
            return;
          }
          
          // 強制削除の確認
          if (!confirm("本当に削除しますか？この操作は取り消せません。")) {
            return;
          }
          
          // 強制削除を実行（同じAPIエンドポイントを使用）
          const forceResponse = await fetch(`/api/posts/${postId}`, {
            method: "DELETE",
            headers: {
              "X-Force-Delete": "true"
            }
          });
          
          if (!forceResponse.ok) {
            const forceData = await forceResponse.json();
            throw new Error(forceData.error || "削除に失敗しました");
          }
        } else {
          throw new Error(data.error || "削除に失敗しました");
        }
      }

      // 成功時は投稿一覧から削除
      setPosts(prev => prev.filter(post => post.id !== postId));
    } catch (error) {
      console.error("Failed to delete post:", error);
      alert(error instanceof Error ? error.message : "削除に失敗しました");
    } finally {
      setDeletingId(null);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("ja-JP", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  if (loading) {
    return (
      <div className="p-6 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="mt-2 text-sm text-gray-600">読み込み中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center">
        <div className="text-red-600 mb-4">
          <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={loadPosts}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          再試行
        </button>
      </div>
    );
  }

  if (posts.length === 0) {
    return (
      <div className="p-6 text-center">
        <div className="text-gray-400 mb-4">
          <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p className="text-gray-600 mb-4">まだ投稿がありません</p>
        <Link
          href="/posts/new"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          新規投稿
        </Link>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-200">
      {posts.map((post) => (
        <div key={post.id} className="p-6 hover:bg-gray-50 transition-colors">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <h3 className="text-lg font-semibold text-gray-900 truncate">
                  <Link 
                    href={`/posts/${post.id}`}
                    className="hover:text-blue-600 transition-colors"
                  >
                    {post.title}
                  </Link>
                </h3>
                {post._count && (post._count.comments > 0 || post._count.bookmarks > 0) && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {post._count.comments > 0 && `${post._count.comments}コメント`}
                    {post._count.comments > 0 && post._count.bookmarks > 0 && "・"}
                    {post._count.bookmarks > 0 && `${post._count.bookmarks}ブックマーク`}
                  </span>
                )}
              </div>
              
              {post.summary && (
                <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                  {post.summary}
                </p>
              )}
              
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span>投稿日: {formatDate(post.created_at)}</span>
                {post.updated_at !== post.created_at && (
                  <span>更新日: {formatDate(post.updated_at)}</span>
                )}
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
            
            <div className="flex items-center gap-2 ml-4">
              <Link
                href={`/posts/${post.id}/edit`}
                className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                編集
              </Link>
              
              <button
                onClick={() => handleDelete(post.id)}
                disabled={deletingId === post.id}
                className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-red-700 bg-white border border-red-300 rounded-md hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {deletingId === post.id ? (
                  <>
                    <div className="w-4 h-4 mr-1 animate-spin rounded-full border-2 border-red-600 border-t-transparent"></div>
                    削除中...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    削除
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
