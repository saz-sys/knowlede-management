"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface LikeRanking {
  post_id: string;
  title: string;
  author_email: string;
  author_name: string;
  created_at: string;
  like_count: number;
}

interface LikeRankingTableProps {
  period: string;
  onPeriodChange: (period: string) => void;
}

export default function LikeRankingTable({ period, onPeriodChange }: LikeRankingTableProps) {
  const [rankings, setRankings] = useState<LikeRanking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  });

  const fetchRankings = async (page: number = 1, periodFilter: string = period) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/rankings/likes?period=${periodFilter}&page=${page}&limit=20`
      );
      
      if (!response.ok) {
        throw new Error("Failed to fetch like rankings");
      }

      const data = await response.json();
      setRankings(data.rankings);
      setPagination(data.pagination);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRankings(1, period);
  }, [period]);

  const handlePageChange = (newPage: number) => {
    fetchRankings(newPage, period);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("ja-JP", {
      year: "numeric",
      month: "short",
      day: "numeric"
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">エラーが発生しました: {error}</p>
        <button
          onClick={() => fetchRankings(1, period)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          再試行
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 期間フィルター */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">期間フィルター</h2>
        </div>
        <div className="flex gap-2">
          {[
            { value: "all", label: "すべて" },
            { value: "day", label: "今日" },
            { value: "week", label: "今週" },
            { value: "month", label: "今月" }
          ].map((option) => (
            <button
              key={option.value}
              onClick={() => onPeriodChange(option.value)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                period === option.value
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* ランキングテーブル */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">いいね数ランキング</h2>
          <p className="text-sm text-gray-600 mt-1">
            {pagination.total}件中 {((pagination.page - 1) * pagination.limit) + 1}-{Math.min(pagination.page * pagination.limit, pagination.total)}件を表示
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  順位
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  タイトル
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  著者
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  いいね数
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  投稿日
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {rankings.map((ranking, index) => (
                <tr key={ranking.post_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    <div className="flex items-center">
                      <span className="text-lg font-bold">
                        {((pagination.page - 1) * pagination.limit) + index + 1}
                      </span>
                      {index < 3 && (
                        <span className="ml-2 text-yellow-500">
                          {index === 0 ? "🥇" : index === 1 ? "🥈" : "🥉"}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="max-w-xs">
                      <Link
                        href={`/posts/${ranking.post_id}`}
                        className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline truncate block"
                      >
                        {ranking.title}
                      </Link>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {ranking.author_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <svg className="w-4 h-4 text-red-500 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm font-medium text-gray-900">
                        {ranking.like_count}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(ranking.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* ページネーション */}
        {pagination.totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-700">
                ページ {pagination.page} / {pagination.totalPages}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handlePageChange(pagination.page - 1)}
                  disabled={pagination.page <= 1}
                  className="px-3 py-2 text-sm font-medium text-gray-500 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  前へ
                </button>
                <button
                  onClick={() => handlePageChange(pagination.page + 1)}
                  disabled={pagination.page >= pagination.totalPages}
                  className="px-3 py-2 text-sm font-medium text-gray-500 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  次へ
                </button>
              </div>
            </div>
          </div>
        )}

        {rankings.length === 0 && !loading && (
          <div className="text-center py-8">
            <p className="text-gray-500">ランキングデータがありません</p>
          </div>
        )}
      </div>
    </div>
  );
}
