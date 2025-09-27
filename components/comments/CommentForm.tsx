"use client";

import { useState } from "react";

interface CommentFormProps {
  onSubmit: (content: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  initialContent?: string;
}

export default function CommentForm({
  onSubmit,
  isLoading = false,
  placeholder = "コメントを入力...",
  initialContent = ""
}: CommentFormProps) {
  const [content, setContent] = useState(initialContent);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || isLoading) return;

    onSubmit(content.trim());
    setContent("");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={placeholder}
          className="w-full p-3 border border-gray-300 rounded-md resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
          disabled={isLoading}
          required
        />
      </div>
      
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={!content.trim() || isLoading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? "投稿中..." : "投稿"}
        </button>
      </div>
    </form>
  );
}
