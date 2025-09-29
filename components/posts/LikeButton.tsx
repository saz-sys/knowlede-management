"use client";

import { useState, useEffect } from "react";
import { useSessionContext } from "@supabase/auth-helpers-react";

interface LikeButtonProps {
  postId: string;
  initialLikeCount?: number;
  initialIsLiked?: boolean;
  className?: string;
  skipInitialCheck?: boolean; // 初期状態チェックをスキップするかどうか
  onToggle?: (isLiked: boolean) => void;
}

interface LikeData {
  likeCount: number;
  isLiked: boolean;
}

export default function LikeButton({ 
  postId, 
  initialLikeCount = 0, 
  initialIsLiked = false,
  className = "",
  skipInitialCheck = false,
  onToggle
}: LikeButtonProps) {
  const { session } = useSessionContext();
  const [likeCount, setLikeCount] = useState(initialLikeCount);
  const [isLiked, setIsLiked] = useState(initialIsLiked);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  // 初期データを取得（skipInitialCheckがfalseの場合のみ）
  useEffect(() => {
    const fetchLikeData = async () => {
      if (!session || isInitialized || skipInitialCheck) return;

      try {
        const response = await fetch(`/api/posts/${postId}/likes`);
        if (response.ok) {
          const data: LikeData = await response.json();
          setLikeCount(data.likeCount);
          setIsLiked(data.isLiked);
        }
      } catch (error) {
        console.error("Failed to fetch like data:", error);
      } finally {
        setIsInitialized(true);
      }
    };

    fetchLikeData();
  }, [session, postId, isInitialized, skipInitialCheck]);

  // skipInitialCheckがtrueの場合は、外部から渡された初期値を直接使用
  useEffect(() => {
    if (skipInitialCheck) {
      setLikeCount(initialLikeCount);
      setIsLiked(initialIsLiked);
      setIsInitialized(true);
    }
  }, [skipInitialCheck, initialLikeCount, initialIsLiked]);

  const handleToggleLike = async (e: React.MouseEvent) => {
    e.stopPropagation(); // 親要素へのイベント伝播を停止
    
    if (!session) {
      alert("ログインが必要です");
      return;
    }

    setIsLoading(true);
    try {
      if (isLiked) {
        // いいねを削除
        const response = await fetch(`/api/posts/${postId}/likes`, {
          method: "DELETE"
        });

        if (response.ok) {
          setIsLiked(false);
          setLikeCount(prev => Math.max(0, prev - 1));
          onToggle?.(false);
        } else {
          throw new Error("いいねの削除に失敗しました");
        }
      } else {
        // いいねを追加
        const response = await fetch(`/api/posts/${postId}/likes`, {
          method: "POST"
        });

        if (response.ok) {
          setIsLiked(true);
          setLikeCount(prev => prev + 1);
          onToggle?.(true);
        } else if (response.status === 409) {
          // 既にいいね済み
          setIsLiked(true);
          onToggle?.(true);
        } else {
          throw new Error("いいねの追加に失敗しました");
        }
      }
    } catch (error) {
      console.error("Like toggle error:", error);
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
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      </button>
    );
  }

  return (
    <button
      onClick={handleToggleLike}
      disabled={isLoading}
      className={`p-2 rounded-md hover:bg-gray-100 transition-colors ${
        isLiked ? "text-red-500" : "text-gray-400 hover:text-red-500"
      } ${className}`}
      title={isLiked ? "いいねを解除" : "いいねする"}
    >
      {isLoading ? (
        <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      ) : (
        <svg 
          className="w-5 h-5" 
          fill={isLiked ? "currentColor" : "none"} 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" 
          />
        </svg>
      )}
    </button>
  );
}
