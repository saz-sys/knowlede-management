"use client";

import { useState } from "react";
import BookmarkList from "@/components/bookmarks/BookmarkList";

type FilterType = "all" | "unread";

export default function BookmarksPage() {
  const [filter, setFilter] = useState<FilterType>("all");

  const filterOptions = [
    { value: "all", label: "すべて" },
    { value: "unread", label: "未読" }
  ];

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold text-gray-900">あとで読む</h1>
        <p className="text-sm text-gray-600">ブックマークした記事を管理できます。</p>
      </header>

      <div className="flex gap-2">
        {filterOptions.map((option) => (
          <button
            key={option.value}
            onClick={() => setFilter(option.value as FilterType)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              filter === option.value
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>

      <BookmarkList filter={filter} />
    </div>
  );
}
