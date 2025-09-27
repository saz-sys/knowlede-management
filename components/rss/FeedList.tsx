"use client";

import { useMemo } from "react";
import clsx from "clsx";
import type { RssFeed } from "@/lib/types/rss";

interface FeedListProps {
  feeds: RssFeed[];
  keyword: string;
  tagFilter: string | null;
  onKeywordChange: (value: string) => void;
  onTagFilterChange: (tag: string | null) => void;
}

export default function FeedList({ feeds, keyword, tagFilter, onKeywordChange, onTagFilterChange }: FeedListProps) {
  const normalizedKeyword = keyword.toLowerCase();

  const availableTags = useMemo(() => {
    const tags = new Set<string>();
    feeds.forEach((feed) => feed.tags?.forEach((tag) => tags.add(tag)));
    return Array.from(tags).sort();
  }, [feeds]);

  const filtered = useMemo(() => {
    return feeds.filter((feed) => {
      if (tagFilter && !feed.tags?.includes(tagFilter)) return false;
      if (normalizedKeyword) {
        const text = `${feed.name} ${feed.url}`.toLowerCase();
        if (!text.includes(normalizedKeyword)) return false;
      }
      return true;
    });
  }, [feeds, normalizedKeyword, tagFilter]);

  return (
    <section className="rounded-lg border bg-white p-5 shadow-sm">
      <header className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">登録済みフィード</h2>
          <p className="text-sm text-gray-500">{filtered.length} 件表示中</p>
        </div>
        <div className="w-full md:w-64">
          <input
            value={keyword}
            onChange={(event) => onKeywordChange(event.target.value)}
            placeholder="キーワードで検索"
            className="block w-full rounded-md border-gray-300 text-sm shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
          />
        </div>
      </header>

      {availableTags.length > 0 && (
        <div className="mt-4">
          <p className="mb-2 text-sm font-medium text-gray-700">タグで絞り込み</p>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => onTagFilterChange(null)}
              className={clsx(
                "rounded-full px-3 py-1 text-sm",
                tagFilter === null ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600"
              )}
            >
              すべて
            </button>
            {availableTags.map((tag) => (
              <button
                key={tag}
                onClick={() => onTagFilterChange(tag)}
                className={clsx(
                  "rounded-full px-3 py-1 text-sm",
                  tagFilter === tag ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600"
                )}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="mt-6 space-y-3">
        {filtered.length === 0 ? (
          <p className="text-sm text-gray-600">条件に一致するフィードはありません。</p>
        ) : (
          filtered.map((feed) => (
            <article key={feed.id} className="rounded-md border border-gray-200 p-4">
              <header className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-semibold text-gray-900">{feed.name}</h3>
                  <p className="text-sm text-blue-600">
                    <a href={feed.url} target="_blank" rel="noopener noreferrer" className="underline">
                      {feed.url}
                    </a>
                  </p>
                </div>
                <span
                  className={clsx(
                    "rounded-full px-2 py-0.5 text-xs font-medium",
                    feed.is_active ? "bg-green-100 text-green-700" : "bg-gray-200 text-gray-600"
                  )}
                >
                  {feed.is_active ? "アクティブ" : "停止中"}
                </span>
              </header>

              <div className="mt-3 flex flex-wrap gap-2 text-xs text-gray-500">
                <span>登録日: {feed.created_at ? new Date(feed.created_at).toLocaleDateString("ja-JP") : "不明"}</span>
                <span>
                  最終取得: {feed.last_fetched_at ? new Date(feed.last_fetched_at).toLocaleString("ja-JP") : "未取得"}
                </span>
              </div>

              <div className="mt-2 flex flex-wrap gap-1">
                {feed.tags?.length ? (
                  feed.tags.map((tag) => (
                    <span key={tag} className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-800">
                      {tag}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-gray-400">タグなし</span>
                )}
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}

