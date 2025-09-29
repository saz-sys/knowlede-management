"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface CommentRanking {
  post_id: string;
  title: string;
  url: string;
  author_email: string;
  author_name: string;
  created_at: string;
  comment_count: number;
}

interface CommentRankingTableProps {
  period: string;
  onPeriodChange: (period: string) => void;
}

export default function CommentRankingTable({ period, onPeriodChange }: CommentRankingTableProps) {
  const [rankings, setRankings] = useState<CommentRanking[]>([]);
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
        `/api/rankings/comments?period=${periodFilter}&page=${page}&limit=20`
      );
      
      if (!response.ok) {
        throw new Error("Failed to fetch comment rankings");
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
      <div className="flex gap-2 mb-4">
        {[
          { value: "all", label: "全期間" },
          { value: "day", label: "今日" },
          { value: "week", label: "今週" },
          { value: "month", label: "今月" }
        ].map(({ value, label }) => (
          <button
            key={value}
            onClick={() => onPeriodChange(value)}
            className={`px-3 py-1 rounded text-sm ${
              period === value
                ? "bg-blue-600 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* ランキングテーブル */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {/* デスクトップ表示 */}
        <div className="hidden md:block">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  順位
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  記事タイトル
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  投稿者
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  投稿日
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  コメント数
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {rankings.map((ranking, index) => (
                <tr key={ranking.post_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {pagination.page === 1 ? index + 1 : (pagination.page - 1) * pagination.limit + index + 1}
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm">
                      <Link
                        href={`/posts/${ranking.post_id}`}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        {ranking.title}
                      </Link>
                      {ranking.url && (
                        <div className="text-xs text-gray-500 mt-1">
                          <a
                            href={ranking.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:text-blue-600"
                          >
                            {ranking.url}
                          </a>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {ranking.author_name || ranking.author_email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(ranking.created_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {ranking.comment_count}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* モバイル表示 */}
        <div className="md:hidden">
          {rankings.map((ranking, index) => (
            <div key={ranking.post_id} className="border-b border-gray-200 p-4 hover:bg-gray-50">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-900">
                    {pagination.page === 1 ? index + 1 : (pagination.page - 1) * pagination.limit + index + 1}位
                  </span>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {ranking.comment_count}コメント
                  </span>
                </div>
              </div>
              
              <div className="mb-2">
                <Link
                  href={`/posts/${ranking.post_id}`}
                  className="text-blue-600 hover:text-blue-800 font-medium text-sm leading-tight"
                >
                  {ranking.title}
                </Link>
                {ranking.url && (
                  <div className="text-xs text-gray-500 mt-1">
                    <a
                      href={ranking.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-blue-600"
                    >
                      {ranking.url}
                    </a>
                  </div>
                )}
              </div>
              
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{ranking.author_name || ranking.author_email}</span>
                <span>{formatDate(ranking.created_at)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ページネーション */}
      {pagination.totalPages > 1 && (
        <div className="flex justify-center items-center space-x-2">
          <button
            onClick={() => handlePageChange(pagination.page - 1)}
            disabled={pagination.page === 1}
            className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            前へ
          </button>
          
          <span className="text-sm text-gray-700">
            {pagination.page} / {pagination.totalPages} ページ
          </span>
          
          <button
            onClick={() => handlePageChange(pagination.page + 1)}
            disabled={pagination.page === pagination.totalPages}
            className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            次へ
          </button>
        </div>
      )}

      {/* 結果サマリー */}
      <div className="text-center text-sm text-gray-600">
        {pagination.total > 0 ? (
          <>
            {pagination.total}件中 {((pagination.page - 1) * pagination.limit) + 1}-
            {Math.min(pagination.page * pagination.limit, pagination.total)}件を表示
          </>
        ) : (
          "コメントがある記事が見つかりませんでした"
        )}
      </div>
    </div>
  );
}
