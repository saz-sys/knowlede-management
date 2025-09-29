"use client";

import { useState, useEffect } from "react";
import type { ResourceLink } from "@/lib/types/resources";

interface MyProfileProps {
  className?: string;
}

export default function MyProfile({ className = "" }: MyProfileProps) {
  const [links, setLinks] = useState<ResourceLink[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/resources/my");
      if (!response.ok) {
        throw new Error("プロフィールの取得に失敗しました");
      }
      const data = await response.json();
      setLinks(data.links || []);
    } catch (error) {
      console.error("Failed to load profile:", error);
      setError(error instanceof Error ? error.message : "プロフィールの取得に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (newLinks: { service: string; url: string }[]) => {
    try {
      const response = await fetch("/api/resources/my", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ links: newLinks })
      });

      if (!response.ok) {
        throw new Error("プロフィールの保存に失敗しました");
      }

      await loadProfile();
      setIsEditing(false);
    } catch (error) {
      console.error("Failed to save profile:", error);
      alert(error instanceof Error ? error.message : "プロフィールの保存に失敗しました");
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  if (loading) {
    return (
      <div className="text-center py-4">
        <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        <p className="mt-2 text-sm text-gray-600">読み込み中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-4">
        <p className="text-red-600 text-sm mb-2">{error}</p>
        <button
          onClick={loadProfile}
          className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
        >
          再試行
        </button>
      </div>
    );
  }

  return (
    <div className={className}>
      {!isEditing ? (
        <div>
          {links.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-gray-600 text-sm mb-3">プロフィールリンクが設定されていません</p>
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
              >
                プロフィールを設定
              </button>
            </div>
          ) : (
            <div>
              <div className="space-y-2 mb-4">
                {links.map((link, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-700">{link.service}</span>
                      <a
                        href={link.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 text-sm truncate"
                      >
                        {link.url}
                      </a>
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={() => setIsEditing(true)}
                className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 text-sm"
              >
                編集
              </button>
            </div>
          )}
        </div>
      ) : (
        <ProfileEditForm
          initialLinks={links}
          onSave={handleSave}
          onCancel={handleCancel}
        />
      )}
    </div>
  );
}

interface ProfileEditFormProps {
  initialLinks: ResourceLink[];
  onSave: (links: { service: string; url: string }[]) => void;
  onCancel: () => void;
}

function ProfileEditForm({ initialLinks, onSave, onCancel }: ProfileEditFormProps) {
  const [links, setLinks] = useState<{ service: string; url: string }[]>(
    initialLinks.length > 0 
      ? initialLinks.map(link => ({ service: link.service, url: link.url }))
      : [{ service: "", url: "" }]
  );

  const handleAddLink = () => {
    setLinks([...links, { service: "", url: "" }]);
  };

  const handleRemoveLink = (index: number) => {
    setLinks(links.filter((_, i) => i !== index));
  };

  const handleLinkChange = (index: number, field: 'service' | 'url', value: string) => {
    const newLinks = [...links];
    newLinks[index][field] = value;
    setLinks(newLinks);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const validLinks = links.filter(link => link.service.trim() && link.url.trim());
    onSave(validLinks);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-3">
        {links.map((link, index) => (
          <div key={index} className="flex gap-2 items-end">
            <div className="flex-1">
              <label className="block text-xs font-medium text-gray-700 mb-1">
                サービス名
              </label>
              <input
                type="text"
                value={link.service}
                onChange={(e) => handleLinkChange(index, 'service', e.target.value)}
                placeholder="例: Zenn, Qiita, Twitter"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div className="flex-1">
              <label className="block text-xs font-medium text-gray-700 mb-1">
                URL
              </label>
              <input
                type="url"
                value={link.url}
                onChange={(e) => handleLinkChange(index, 'url', e.target.value)}
                placeholder="https://..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            {links.length > 1 && (
              <button
                type="button"
                onClick={() => handleRemoveLink(index)}
                className="px-2 py-2 text-red-600 hover:text-red-800"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            )}
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={handleAddLink}
        className="w-full px-3 py-2 border border-dashed border-gray-300 rounded-md text-gray-600 hover:border-gray-400 hover:text-gray-700 text-sm"
      >
        + リンクを追加
      </button>

      <div className="flex gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 text-sm"
        >
          キャンセル
        </button>
        <button
          type="submit"
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
        >
          保存
        </button>
      </div>
    </form>
  );
}
