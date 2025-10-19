"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface RankingItem {
  id: string;
  title: string;
  count: number;
  author_email?: string;
}

interface Rankings {
  bookmarks: RankingItem[];
  likes: RankingItem[];
  comments: RankingItem[];
}

export default function RankingSidebar() {
  const [rankings, setRankings] = useState<Rankings>({
    bookmarks: [],
    likes: [],
    comments: []
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchRankings = async () => {
      try {
        setIsLoading(true);
        const [bookmarksRes, likesRes, commentsRes] = await Promise.all([
          fetch("/api/rankings/bookmarks?limit=3"),
          fetch("/api/rankings/likes?limit=3"),
          fetch("/api/rankings/comments?limit=3")
        ]);

        const [bookmarks, likes, comments] = await Promise.all([
          bookmarksRes.ok ? bookmarksRes.json() : { rankings: [] },
          likesRes.ok ? likesRes.json() : { rankings: [] },
          commentsRes.ok ? commentsRes.json() : { rankings: [] }
        ]);

        setRankings({
          bookmarks: bookmarks.rankings || [],
          likes: likes.rankings || [],
          comments: comments.rankings || []
        });
      } catch (error) {
        console.error("Failed to fetch rankings:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRankings();
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="ocean-card p-4">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
              <div className="space-y-2">
                {[1, 2, 3].map((j) => (
                  <div key={j} className="h-3 bg-gray-200 rounded w-full"></div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ブックマークランキング */}
      <div className="ocean-card p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">ブックマーク</h3>
          <Link 
            href="/rankings/bookmarks" 
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            すべて見る
          </Link>
        </div>
        <div className="space-y-2">
          {rankings.bookmarks.length > 0 ? (
            rankings.bookmarks.map((item, index) => (
              <div key={item.id} className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <Link 
                    href={`/posts/${item.id}`}
                    className="text-sm text-gray-900 hover:text-blue-600 line-clamp-2"
                  >
                    {item.title}
                  </Link>
                  <div className="text-xs text-gray-500 mt-1">
                    {item.author_email || "不明"}
                  </div>
                </div>
                <div className="flex items-center ml-2">
                  <span className="text-sm font-medium text-gray-600">
                    {item.count}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="text-sm text-gray-500">データがありません</div>
          )}
        </div>
      </div>

      {/* いいねランキング */}
      <div className="ocean-card p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">いいね</h3>
          <Link 
            href="/rankings/likes" 
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            すべて見る
          </Link>
        </div>
        <div className="space-y-2">
          {rankings.likes.length > 0 ? (
            rankings.likes.map((item, index) => (
              <div key={item.id} className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <Link 
                    href={`/posts/${item.id}`}
                    className="text-sm text-gray-900 hover:text-blue-600 line-clamp-2"
                  >
                    {item.title}
                  </Link>
                  <div className="text-xs text-gray-500 mt-1">
                    {item.author_email || "不明"}
                  </div>
                </div>
                <div className="flex items-center ml-2">
                  <span className="text-sm font-medium text-gray-600">
                    {item.count}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="text-sm text-gray-500">データがありません</div>
          )}
        </div>
      </div>

      {/* コメントランキング */}
      <div className="ocean-card p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">コメント</h3>
          <Link 
            href="/rankings/comments" 
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            すべて見る
          </Link>
        </div>
        <div className="space-y-2">
          {rankings.comments.length > 0 ? (
            rankings.comments.map((item, index) => (
              <div key={item.id} className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <Link 
                    href={`/posts/${item.id}`}
                    className="text-sm text-gray-900 hover:text-blue-600 line-clamp-2"
                  >
                    {item.title}
                  </Link>
                  <div className="text-xs text-gray-500 mt-1">
                    {item.author_email || "不明"}
                  </div>
                </div>
                <div className="flex items-center ml-2">
                  <span className="text-sm font-medium text-gray-600">
                    {item.count}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="text-sm text-gray-500">データがありません</div>
          )}
        </div>
      </div>
    </div>
  );
}
