"use client";

import { FormEvent, useState } from "react";

interface FeedFormProps {
  onSubmitted?: () => void;
}

export default function FeedForm({ onSubmitted }: FeedFormProps) {
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [tags, setTags] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const resetForm = () => {
    setName("");
    setUrl("");
    setTags("");
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!name.trim() || !url.trim()) {
      alert("フィード名とURLは必須です");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch("/api/rss-feeds", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          name: name.trim(),
          url: url.trim(),
          tags: tags
            .split(",")
            .map((tag) => tag.trim())
            .filter((tag) => tag.length > 0)
        })
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.error ?? "フィードの追加に失敗しました");
      }

      resetForm();
      onSubmitted?.();
    } catch (error) {
      alert(error instanceof Error ? error.message : "フィードの追加に失敗しました");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="rounded-lg border bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900">新しいRSSフィードを追加</h2>
      <p className="mt-1 text-sm text-gray-500">URLと任意のタグを入力してフィードを登録できます。</p>

      <form onSubmit={handleSubmit} className="mt-4 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">フィード名</label>
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            placeholder="例) TechCrunch"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">RSS URL</label>
          <input
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            placeholder="https://example.com/feed.xml"
            type="url"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">タグ (カンマ区切り)</label>
          <input
            value={tags}
            onChange={(event) => setTags(event.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            placeholder="AI, Infrastructure"
          />
        </div>

        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={resetForm}
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100"
          >
            クリア
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded-md bg-blue-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? "登録中..." : "フィードを追加"}
          </button>
        </div>
      </form>
    </section>
  );
}

