"use client";

import { useState } from "react";
import CommentRankingTable from "@/components/rankings/CommentRankingTable";

export default function CommentRankingPage() {
  const [period, setPeriod] = useState("all");

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* ヘッダー */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            コメント数ランキング
          </h1>
          <p className="text-gray-600">
            コメント数が多い記事をランキング形式で表示します。期間を絞り込んで確認できます。
          </p>
        </div>

        {/* ランキングテーブル */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">
              コメント数ランキング
            </h2>
          </div>
          <div className="p-6">
            <CommentRankingTable
              period={period}
              onPeriodChange={setPeriod}
            />
          </div>
        </div>

        {/* 説明 */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-2">
            ランキングについて
          </h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• コメント数は投稿に対するコメントの総数を表示します</li>
            <li>• 期間フィルターで「今日」「今週」「今月」のランキングを確認できます</li>
            <li>• 記事タイトルをクリックすると詳細ページに移動します</li>
            <li>• 外部リンクがある場合は、元記事へのリンクも表示されます</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
