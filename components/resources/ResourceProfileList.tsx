"use client";

import { useState } from "react";
import type { ResourceLinkGroup } from "@/lib/types/resources";

interface ResourceProfileListProps {
  groups: ResourceLinkGroup[];
  onEdit: (group: ResourceLinkGroup) => void;
}

const SERVICE_LABELS: Record<string, string> = {
  zenn: "Zenn",
  qiita: "Qiita",
  note: "note",
  github: "GitHub",
  x: "X (旧Twitter)",
  other: "その他"
};

export default function ResourceProfileList({ groups, onEdit }: ResourceProfileListProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (groups.length === 0) {
    return (
      <section className="rounded-lg border border-dashed bg-white p-8 text-center text-sm text-gray-500 shadow-sm">
        登録されたリソースがありません。上のフォームから追加できます。
      </section>
    );
  }

  return (
    <section className="space-y-4">
      {groups.map((group) => {
        const isExpanded = expandedId === group.user_id;
        return (
          <article key={group.user_id} className="rounded-lg border border-gray-200 bg白 p-5 shadow-sm">
            <header className="flex flex-wrap items-center justify-between gap-3">
              <div className="space-y-1">
                <h2 className="text-lg font-semibold text-gray-900">{group.user_name}</h2>
                <p className="text-xs text-gray-500">{group.user_email}</p>
                <p className="text-xs text-gray-500">リンク数: {group.links.length}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => setExpandedId(isExpanded ? null : group.user_id)}
                  className="rounded-md border border-gray-300 px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-100"
                >
                  {isExpanded ? "リンクを閉じる" : `リンクを見る (${group.links.length})`}
                </button>
                <button
                  type="button"
                  onClick={() => onEdit(group)}
                  className="rounded-md border border-blue-200 px-3 py-1.5 text-xs text-blue-600 hover:bg-blue-50"
                >
                  編集
                </button>
              </div>
            </header>

            {isExpanded && (
              <div className="mt-4 space-y-3">
                {group.links.length === 0 ? (
                  <p className="text-sm text-gray-500">登録されたリンクがありません。</p>
                ) : (
                  group.links.map((link) => (
                    <div key={link.id} className="rounded-md border border-gray-200 bg-gray-50 p-4">
                      <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                        <div className="space-y-1">
                          <h3 className="font-medium text-gray-900">{SERVICE_LABELS[link.service] ?? link.service}</h3>
                          <a
                            href={link.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:text-blue-800"
                          >
                            {link.url}
                          </a>
                        </div>
                        <div className="flex flex-col items-start gap-2 text-xs text-gray-500">
                          <span>登録: {new Date(link.created_at).toLocaleDateString("ja-JP")}</span>
                          <span>更新: {new Date(link.updated_at).toLocaleDateString("ja-JP")}</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </article>
        );
      })}
    </section>
  );
}

