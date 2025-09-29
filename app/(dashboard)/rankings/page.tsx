"use client";

import Link from "next/link";

export default function RankingsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* ヘッダー */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            ランキング
          </h1>
          <p className="text-gray-600">
            人気の記事をランキング形式で確認できます。コメント数やブックマーク数で記事の人気度を把握しましょう。
          </p>
        </div>

        {/* ランキング一覧 */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* コメント数ランキング */}
          <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <h2 className="text-xl font-semibold text-gray-900">コメント数ランキング</h2>
                  <p className="text-sm text-gray-600">コメント数が多い記事</p>
                </div>
              </div>
              <p className="text-gray-600 mb-6">
                記事に対するコメント数が多い順にランキング表示します。議論が活発な記事を発見できます。
              </p>
              <Link
                href="/rankings/comments"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
              >
                コメント数ランキングを見る
                <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>
          </div>

          {/* ブックマーク数ランキング */}
          <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <h2 className="text-xl font-semibold text-gray-900">ブックマーク数ランキング</h2>
                  <p className="text-sm text-gray-600">ブックマーク数が多い記事</p>
                </div>
              </div>
              <p className="text-gray-600 mb-6">
                記事がブックマークされた回数が多い順にランキング表示します。多くの人が保存した記事を発見できます。
              </p>
              <Link
                href="/rankings/bookmarks"
                className="inline-flex items-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition-colors"
              >
                ブックマーク数ランキングを見る
                <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>
          </div>
        </div>

        {/* 説明セクション */}
        <div className="mt-12 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            ランキング機能について
          </h3>
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-2">コメント数ランキング</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• 記事に対するコメント数でランキング</li>
                <li>• 議論が活発な記事を発見</li>
                <li>• 期間別フィルター（今日、今週、今月）</li>
                <li>• ページネーション対応</li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-2">ブックマーク数ランキング</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• 記事のブックマーク数でランキング</li>
                <li>• 多くの人が保存した記事を発見</li>
                <li>• 期間別フィルター（今日、今週、今月）</li>
                <li>• ページネーション対応</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
