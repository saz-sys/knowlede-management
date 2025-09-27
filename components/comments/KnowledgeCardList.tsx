"use client";

import { KnowledgeCard } from "@/lib/types/knowledge-cards";

interface KnowledgeCardListProps {
  cards: KnowledgeCard[];
}

export default function KnowledgeCardList({
  cards
}: KnowledgeCardListProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("ja-JP");
  };

  if (cards.length === 0) {
    return (
      <div className="mt-6 p-4 border border-gray-200 rounded-lg bg-gray-50">
        <p className="text-gray-600 text-center">
          まだナレッジカードが作成されていません。
        </p>
      </div>
    );
  }

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-4">ナレッジカード</h3>
      
      <div className="space-y-4">
        {cards.map((card) => (
          <div key={card.id} className="border border-gray-200 rounded-lg p-4 bg-white shadow-sm">
            <div className="flex items-start justify-between mb-2">
              <h4 className="text-lg font-medium text-gray-900">{card.title}</h4>
              <span className="text-xs text-gray-500">
                {formatDate(card.created_at)}
              </span>
            </div>
            
            <div className="prose prose-sm max-w-none mb-3">
              <p className="whitespace-pre-wrap text-gray-700">{card.content}</p>
            </div>
            
            <div className="flex items-center justify-between text-sm text-gray-500">
              <span>
                作成者ID: {card.created_by}
              </span>
              {card.related_comment_ids && card.related_comment_ids.length > 0 && (
                <span>
                  関連コメント: {card.related_comment_ids.length}件
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
