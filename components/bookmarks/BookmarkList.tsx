"use client";

import { useState, useEffect } from "react";
import { useSessionContext } from "@supabase/auth-helpers-react";

interface Bookmark {
  id: string;
  created_at: string;
  is_read: boolean;
  notes: string | null;
  posts: {
    id: string;
    title: string;
    url: string;
    summary: string | null;
    created_at: string;
    metadata: any;
  };
}

interface BookmarkListProps {
  filter?: "all" | "unread";
  className?: string;
}

export default function BookmarkList({ filter = "all", className = "" }: BookmarkListProps) {
  const { session } = useSessionContext();
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadBookmarks = async () => {
    if (!session) return;

    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (filter === "unread") {
        params.append("is_read", "false");
      }

      const response = await fetch(`/api/bookmarks?${params.toString()}`);
      if (!response.ok) {
        throw new Error("ブックマークの取得に失敗しました");
      }

      const { bookmarks: data } = await response.json();
      setBookmarks(data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "エラーが発生しました");
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkAsRead = async (bookmarkId: string) => {
    try {
      const response = await fetch(`/api/bookmarks/${bookmarkId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ is_read: true })
      });

      if (response.ok) {
        setBookmarks(prev => 
          prev.map(b => b.id === bookmarkId ? { ...b, is_read: true } : b)
        );
      }
    } catch (error) {
      console.error("Mark as read error:", error);
    }
  };

  const handleDelete = async (bookmarkId: string) => {
    try {
      const response = await fetch(`/api/bookmarks/${bookmarkId}`, {
        method: "DELETE"
      });

      if (response.ok) {
        setBookmarks(prev => prev.filter(b => b.id !== bookmarkId));
      }
    } catch (error) {
      console.error("Delete bookmark error:", error);
    }
  };

  useEffect(() => {
    loadBookmarks();
  }, [session, filter]);

  if (!session) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">ログインが必要です</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="text-gray-600 mt-2">読み込み中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">{error}</p>
        <button 
          onClick={loadBookmarks}
          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          再試行
        </button>
      </div>
    );
  }

  if (bookmarks.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">
          {filter === "unread" ? "未読のブックマークはありません" : "ブックマークはありません"}
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {bookmarks.map((bookmark) => (
        <div 
          key={bookmark.id} 
          className={`border rounded-lg p-4 bg-white shadow-sm ${
            bookmark.is_read ? "opacity-60" : ""
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-2">
                <a 
                  href={bookmark.posts.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-blue-600"
                >
                  {bookmark.posts.title}
                </a>
              </h3>
              
              {bookmark.posts.summary && (
                <p className="text-gray-600 text-sm mb-2 line-clamp-2">
                  {bookmark.posts.summary}
                </p>
              )}

              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span>
                  追加: {new Date(bookmark.created_at).toLocaleDateString("ja-JP")}
                </span>
                {bookmark.is_read && (
                  <span className="text-green-600">既読</span>
                )}
              </div>

              {bookmark.notes && (
                <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                  <strong>メモ:</strong> {bookmark.notes}
                </div>
              )}
            </div>

            <div className="flex items-center gap-2 ml-4">
              {!bookmark.is_read && (
                <button
                  onClick={() => handleMarkAsRead(bookmark.id)}
                  className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
                >
                  既読にする
                </button>
              )}
              <button
                onClick={() => handleDelete(bookmark.id)}
                className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
              >
                削除
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
