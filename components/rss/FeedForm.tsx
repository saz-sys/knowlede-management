"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";

interface FeedFormProps {
  initialValues?: {
    id: string;
    name: string;
    url: string;
    tags: string[];
    is_active: boolean;
  } | null;
  onSubmitted?: () => void;
  onCancelEdit?: () => void;
}

export default function FeedForm({ initialValues, onSubmitted, onCancelEdit }: FeedFormProps) {
  const [name, setName] = useState(initialValues?.name ?? "");
  const [url, setUrl] = useState(initialValues?.url ?? "");
  const [tags, setTags] = useState(initialValues?.tags?.join(", ") ?? "");
  const [isActive, setIsActive] = useState(initialValues?.is_active ?? true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const resetForm = useCallback(() => {
    setName("");
    setUrl("");
    setTags("");
    setIsActive(true);
  }, []);

  useEffect(() => {
    if (initialValues) {
      setName(initialValues.name);
      setUrl(initialValues.url);
      setTags(initialValues.tags?.join(", ") ?? "");
      setIsActive(initialValues.is_active);
    } else {
      resetForm();
    }
  }, [initialValues, resetForm]);

  const handleCancel = () => {
    if (initialValues) {
      onCancelEdit?.();
    } else {
      resetForm();
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!name.trim() || !url.trim()) {
      alert("フィード名とURLは必須です");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        name: name.trim(),
        url: url.trim(),
        tags: tags
          .split(",")
          .map((tag) => tag.trim())
          .filter((tag) => tag.length > 0),
        is_active: isActive
      };

      const response = initialValues
        ? await fetch("/api/rss-feeds", {
            method: "PATCH",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({ id: initialValues.id, ...payload })
          })
        : await fetch("/api/rss-feeds", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
          });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.error ?? "フィードの保存に失敗しました");
      }

      onSubmitted?.();
      if (!initialValues) {
        resetForm();
      }
    } catch (error) {
      alert(error instanceof Error ? error.message : "フィードの保存に失敗しました");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="rounded-lg border bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900">
        {initialValues ? "RSSフィードを編集" : "新しいRSSフィードを追加"}
      </h2>
      <p className="mt-1 text-sm text-gray-500">
        URLと任意のタグを入力してフィードを{initialValues ? "更新" : "登録"}できます。
      </p>

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

        <div className="flex items-center gap-2">
          <input
            id="feed-active"
            type="checkbox"
            checked={isActive}
            onChange={(event) => setIsActive(event.target.checked)}
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label htmlFor="feed-active" className="text-sm text-gray-700">
            フィードをアクティブにする
          </label>
        </div>

        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={handleCancel}
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100"
          >
            {initialValues ? "キャンセル" : "クリア"}
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded-md bg-blue-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? "保存中..." : initialValues ? "フィードを更新" : "フィードを追加"}
          </button>
        </div>
      </form>
    </section>
  );
}

