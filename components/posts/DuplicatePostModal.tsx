"use client";

import { useState } from "react";
import Link from "next/link";

interface ExistingPost {
  id: string;
  title: string;
  author_email: string;
  created_at: string;
}

interface DuplicatePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  existingPost: ExistingPost | null;
  onViewExisting: () => void;
}

export default function DuplicatePostModal({
  isOpen,
  onClose,
  existingPost,
  onViewExisting
}: DuplicatePostModalProps) {
  if (!isOpen || !existingPost) return null;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("ja-JP", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* オーバーレイ */}
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
        />
        
        {/* モーダル */}
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full">
          <div className="p-6">
            {/* ヘッダー */}
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                重複URLが検出されました
              </h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* 内容 */}
            <div className="mb-6">
              <p className="text-sm text-gray-600 mb-4">
                このURLは既に投稿されています。既存の投稿を確認しますか？
              </p>
              
              <div className="bg-gray-50 rounded-lg p-4 border">
                <h4 className="font-medium text-gray-900 mb-2">
                  {existingPost.title}
                </h4>
                <div className="text-sm text-gray-600 space-y-1">
                  <p>
                    <span className="font-medium">投稿者:</span> {existingPost.author_email}
                  </p>
                  <p>
                    <span className="font-medium">投稿日:</span> {formatDate(existingPost.created_at)}
                  </p>
                </div>
              </div>
            </div>

            {/* アクションボタン */}
            <div className="flex gap-3 justify-end">
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              >
                キャンセル
              </button>
              <Link
                href={`/posts/${existingPost.id}`}
                onClick={onViewExisting}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
              >
                既存投稿を確認
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
