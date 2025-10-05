"use client";

import { useState } from "react";
import LikeRankingTable from "@/components/rankings/LikeRankingTable";

export default function LikeRankingPage() {
  const [period, setPeriod] = useState("all");

  const handlePeriodChange = (newPeriod: string) => {
    setPeriod(newPeriod);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* ヘッダー */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            いいね数ランキング
          </h1>
          <p className="text-gray-600">
            投稿に付けられたいいね数が多い順にランキング表示します。多くの人に評価された記事を発見できます。
          </p>
        </div>

        {/* ランキングテーブル */}
        <LikeRankingTable 
          period={period} 
          onPeriodChange={handlePeriodChange} 
        />
      </div>
    </div>
  );
}
