"use client";

import { useState, useEffect } from "react";
import { useSessionContext } from "@supabase/auth-helpers-react";

interface BookmarkButtonProps {
  postId: string;
  isBookmarked?: boolean;
  onToggle?: (isBookmarked: boolean) => void;
  className?: string;
  skipInitialCheck?: boolean; // 初期状態チェックをスキップするかどうか
}

export default function BookmarkButton({ 
  postId, 
  isBookmarked = false, 
  onToggle,
  className = "",
  skipInitialCheck = false
}: BookmarkButtonProps) {
  const { session } = useSessionContext();
  const [isLoading, setIsLoading] = useState(false);
  const [bookmarked, setBookmarked] = useState(isBookmarked);
  const [isInitialized, setIsInitialized] = useState(false);

  // 初期状態を取得（skipInitialCheckがfalseの場合のみ）
  useEffect(() => {
    const checkBookmarkStatus = async () => {
      if (!session || isInitialized || skipInitialCheck) return;

      try {
        const response = await fetch(`/api/bookmarks?post_id=${postId}`);
        if (response.ok) {
          const { bookmarks } = await response.json();
          const isBookmarked = bookmarks && bookmarks.length > 0;
          setBookmarked(isBookmarked);
        }
      } catch (error) {
        console.error("Failed to check bookmark status:", error);
      } finally {
        setIsInitialized(true);
      }
    };

    checkBookmarkStatus();
  }, [session, postId, isInitialized, skipInitialCheck]);

  // skipInitialCheckがtrueの場合は、外部から渡されたisBookmarkedを直接使用
  useEffect(() => {
    if (skipInitialCheck) {
      setBookmarked(isBookmarked);
      setIsInitialized(true);
    }
  }, [skipInitialCheck, isBookmarked]);

  const handleToggle = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!session) {
      alert("ログインが必要です");
      return;
    }

    setIsLoading(true);
    try {
      if (bookmarked) {
        // ブックマーク解除
        const response = await fetch(`/api/bookmarks?post_id=${postId}`, {
          method: "DELETE"
        });

        if (response.ok) {
          setBookmarked(false);
          onToggle?.(false);
        } else {
          const errorData = await response.json().catch(() => null);
          const errorMessage = errorData?.error || "ブックマークの解除に失敗しました";
          throw new Error(errorMessage);
        }
      } else {
        // ブックマーク登録
        const response = await fetch("/api/bookmarks", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ post_id: postId })
        });

        if (response.ok) {
          setBookmarked(true);
          onToggle?.(true);
        } else {
          const errorData = await response.json().catch(() => null);
          const errorMessage = errorData?.error || "ブックマークの登録に失敗しました";
          throw new Error(errorMessage);
        }
      }
    } catch (error) {
      console.error("Bookmark toggle error:", error);
      alert(error instanceof Error ? error.message : "エラーが発生しました");
    } finally {
      setIsLoading(false);
    }
  };

  if (!session) {
    return null;
  }

  // 初期化中は薄い表示
  if (!isInitialized) {
    return (
      <button
        disabled
        className={`p-2 rounded-md transition-colors text-gray-300 ${className}`}
        title="読み込み中..."
      >
        <svg 
          className="w-5 h-5" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" 
          />
        </svg>
      </button>
    );
  }

  return (
    <button
      onClick={handleToggle}
      disabled={isLoading}
      className={`p-2 rounded-md hover:bg-gray-100 transition-colors ${
        bookmarked ? "text-yellow-500" : "text-gray-400 hover:text-yellow-500"
      } ${className}`}
      title={bookmarked ? "ブックマークを解除" : "あとで読むに追加"}
    >
      {isLoading ? (
        <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      ) : (
        <svg 
          className="w-5 h-5" 
          fill={bookmarked ? "currentColor" : "none"} 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" 
          />
        </svg>
      )}
    </button>
  );
}
