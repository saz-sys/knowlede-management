"use client";

import { useState } from "react";

interface KnowledgeCardFormProps {
  postId: string;
  relatedCommentIds?: string[];
}

export default function KnowledgeCardForm({
  postId,
  relatedCommentIds = []
}: KnowledgeCardFormProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim() || isLoading) return;

    setIsLoading(true);
    try {
      const response = await fetch("/api/knowledge-cards", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          post_id: postId,
          title: title.trim(),
          content: content.trim(),
          related_comment_ids: relatedCommentIds,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create knowledge card");
      }

      setTitle("");
      setContent("");
      setIsOpen(false);
      window.location.reload();
    } catch (error) {
      console.error("Error creating knowledge card:", error);
      alert("ナレッジカードの作成に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <div className="mt-4">
        <button
          onClick={() => setIsOpen(true)}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
        >
          ナレッジカードを作成
        </button>
      </div>
    );
  }

  return (
    <div className="mt-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
      <h4 className="text-lg font-semibold mb-4">ナレッジカード作成</h4>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            タイトル
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
            placeholder="ナレッジカードのタイトルを入力..."
            required
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
            内容
          </label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md resize-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            rows={6}
            placeholder="議論の要約や重要なポイントを入力..."
            required
            disabled={isLoading}
          />
        </div>

        {relatedCommentIds.length > 0 && (
          <div className="text-sm text-gray-600">
            <p>関連コメント: {relatedCommentIds.length}件</p>
          </div>
        )}

        <div className="flex gap-2">
          <button
            type="submit"
            disabled={!title.trim() || !content.trim() || isLoading}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? "作成中..." : "作成"}
          </button>
          <button
            type="button"
            onClick={() => {
              setIsOpen(false);
              setTitle("");
              setContent("");
            }}
            className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
            disabled={isLoading}
          >
            キャンセル
          </button>
        </div>
      </form>
    </div>
  );
}
