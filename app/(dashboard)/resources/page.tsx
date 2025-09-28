"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { ResourceLink, ResourceLinkGroup } from "@/lib/types/resources";
import ResourceProfileForm from "@/components/resources/ResourceProfileForm";
import ResourceProfileList from "@/components/resources/ResourceProfileList";

async function fetchResourceLinks(): Promise<ResourceLink[]> {
  const response = await fetch("/api/resources");
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(data?.error ?? "リソースの取得に失敗しました");
  }
  const { links } = await response.json();
  return links as ResourceLink[];
}

async function fetchUsers(): Promise<{ id: string; email: string; name: string }[]> {
  const response = await fetch("/api/users");
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(data?.error ?? "ユーザー一覧の取得に失敗しました");
  }
  const { users } = await response.json();
  return users as { id: string; email: string; name: string }[];
}

function groupLinksByUser(links: ResourceLink[]): ResourceLinkGroup[] {
  const map = new Map<string, ResourceLinkGroup>();
  links.forEach((link) => {
    if (!map.has(link.user_id)) {
      map.set(link.user_id, {
        user_id: link.user_id,
        user_name: link.user_name,
        user_email: link.user_email,
        links: []
      });
    }
    map.get(link.user_id)!.links.push(link);
  });
  return Array.from(map.values());
}

export default function ResourceDirectoryPage() {
  const [groups, setGroups] = useState<ResourceLinkGroup[]>([]);
  const [users, setUsers] = useState<{ id: string; email: string; name: string }[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingGroup, setEditingGroup] = useState<ResourceLinkGroup | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [links, users] = await Promise.all([fetchResourceLinks(), fetchUsers()]);
      setGroups(groupLinksByUser(links));
      setUsers(users);
    } catch (err) {
      setError(err instanceof Error ? err.message : "リソースの取得に失敗しました");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const userOptions = useMemo(
    () => users.map((user) => ({ id: user.id, email: user.email, name: user.name })),
    [users]
  );

  const handleCompleted = async () => {
    setEditingGroup(null);
    await loadData();
  };

  return (
    <div className="min-h-screen">
      <main className="mx-auto max-w-3xl space-y-6 px-4 py-8">
        <header className="space-y-2">
          <h1 className="text-3xl font-bold ocean-text">👥 プロフィール一覧</h1>
          <p className="text-sm text-gray-600">
            チームメンバーのプロフィールリンクを確認できます。
          </p>
        </header>

        <ResourceProfileForm
          key={editingGroup?.user_id ?? "new"}
          initialValues={editingGroup ? {
            user_id: editingGroup.user_id,
            links: editingGroup.links.map((link) => ({ service: link.service, url: link.url }))
          } : undefined}
          onCompleted={handleCompleted}
          onCancel={() => setEditingGroup(null)}
          users={userOptions}
          isEditing={Boolean(editingGroup)}
        />

        {isLoading ? (
          <section className="rounded-lg border bg-white p-8 text-center text-sm text-gray-600 shadow-sm">
            読み込み中です…
          </section>
        ) : error ? (
          <section className="rounded-lg border bg白 p-8 text-center text-sm text-red-600 shadow-sm">
            {error}
          </section>
        ) : (
          <ResourceProfileList groups={groups} onEdit={setEditingGroup} />
        )}
      </main>
    </div>
  );
}

