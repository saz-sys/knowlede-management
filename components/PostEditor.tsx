"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

interface PostEditorProps {
  onSuccess?: (postId: string) => void;
}

const initialState = {
  title: "",
  url: "",
  summary: "",
  content: "",
  tags: "",
  notifyChannels: ""
};

export default function PostEditor({ onSuccess }: PostEditorProps) {
  const [form, setForm] = useState(initialState);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const router = useRouter();

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage(null);

    if (!form.title.trim() || !form.url.trim()) {
      setErrorMessage("タイトルとURLは必須です");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch("/api/posts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          title: form.title.trim(),
          url: form.url.trim(),
          summary: form.summary.trim() || undefined,
          content: form.content.trim() || undefined,
          tags: form.tags
            .split(",")
            .map((tag) => tag.trim())
            .filter((tag) => tag.length > 0),
          notified_channels: form.notifyChannels
            .split(",")
            .map((channel) => channel.trim())
            .filter((channel) => channel.length > 0)
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "投稿に失敗しました");
      }

      const { post } = await response.json();

      setForm(initialState);

      if (onSuccess) {
        onSuccess(post.id);
      } else {
        router.push(`/posts/${post.id}`);
      }
    } catch (error) {
      console.error("Failed to create post", error);
      setErrorMessage(error instanceof Error ? error.message : "投稿に失敗しました");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          タイトル <span className="text-red-500">*</span>
        </label>
        <input
          id="title"
          name="title"
          type="text"
          required
          value={form.title}
          onChange={handleChange}
          placeholder="投稿タイトル"
          className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring"
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="url" className="block text-sm font-medium text-gray-700">
          記事URL <span className="text-red-500">*</span>
        </label>
        <input
          id="url"
          name="url"
          type="url"
          required
          value={form.url}
          onChange={handleChange}
          placeholder="https://example.com/article"
          className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring"
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="summary" className="block text-sm font-medium text-gray-700">
          要約
        </label>
        <textarea
          id="summary"
          name="summary"
          value={form.summary}
          onChange={handleChange}
          placeholder="記事の要約やポイント"
          rows={3}
          className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring"
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="content" className="block text-sm font-medium text-gray-700">
          コメント / 所感
        </label>
        <textarea
          id="content"
          name="content"
          value={form.content}
          onChange={handleChange}
          placeholder="自身のコメントや補足"
          rows={6}
          className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring"
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700">
          タグ（カンマ区切り）
        </label>
        <input
          id="tags"
          name="tags"
          value={form.tags}
          onChange={handleChange}
          placeholder="nextjs, supabase, rss"
          className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring"
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="notifyChannels" className="block text-sm font-medium text-gray-700">
          Slack通知チャンネル（カンマ区切り・任意）
        </label>
        <input
          id="notifyChannels"
          name="notifyChannels"
          value={form.notifyChannels}
          onChange={handleChange}
          placeholder="#engineering, #pde-knowledge"
          className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring"
        />
      </div>

      {errorMessage && (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {errorMessage}
        </div>
      )}

      <div className="flex justify-end gap-3">
        <button
          type="button"
          onClick={() => router.back()}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          キャンセル
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? "投稿中..." : "投稿する"}
        </button>
      </div>
    </form>
  );
}

