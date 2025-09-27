"use client";

import { useCallback, useEffect, useState } from "react";
import FeedForm from "@/components/rss/FeedForm";
import FeedList from "@/components/rss/FeedList";
import type { RssFeed } from "@/lib/types/rss";

async function fetchFeeds() {
  const response = await fetch("/api/rss-feeds");
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(data?.error ?? "RSSフィードの取得に失敗しました");
  }
  const { feeds } = await response.json();
  return feeds as RssFeed[];
}

export default function RssFeedsPage() {
  const [feeds, setFeeds] = useState<RssFeed[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [keyword, setKeyword] = useState("");
  const [tagFilter, setTagFilter] = useState<string | null>(null);

  const loadFeeds = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchFeeds();
      setFeeds(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "RSSフィードの取得に失敗しました");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFeeds();
  }, [loadFeeds]);

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold text-gray-900">RSSフィード管理</h1>
        <p className="text-sm text-gray-600">登録済みフィードの確認と新規追加ができます。</p>
      </header>

      <FeedForm onSubmitted={loadFeeds} />

      {isLoading ? (
        <section className="rounded-lg border bg-white p-5 text-sm text-gray-600 shadow-sm">
          読み込み中です…
        </section>
      ) : error ? (
        <section className="rounded-lg border bg-white p-5 text-sm text-red-600 shadow-sm">
          {error}
        </section>
      ) : (
        <FeedList
          feeds={feeds}
          keyword={keyword}
          tagFilter={tagFilter}
          onKeywordChange={setKeyword}
          onTagFilterChange={setTagFilter}
        />
      )}
    </div>
  );
}

