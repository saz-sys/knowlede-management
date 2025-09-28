"use client";

import { useCallback, useEffect, useState } from "react";

interface ResourceProfileFormProps {
  initialValues?: ResourceProfileFormValues;
  onCompleted: () => void;
  onCancel: () => void;
  users: { id: string; email: string; name: string }[];
  isEditing?: boolean;
}

export interface ResourceProfileFormValues {
  user_id: string;
  links: ResourceLinkFormValues[];
}

export interface ResourceLinkFormValues {
  id?: string;
  service: string;
  url: string;
}

function emptyProfile(): ResourceProfileFormValues {
  return {
    user_id: "",
    links: []
  };
}

interface FormState {
  values: ResourceProfileFormValues;
  submitting: boolean;
  error: string | null;
}

const SERVICE_OPTIONS = [
  { value: "zenn", label: "Zenn" },
  { value: "qiita", label: "Qiita" },
  { value: "note", label: "note" },
  { value: "github", label: "GitHub" },
  { value: "x", label: "X (旧Twitter)" },
  { value: "other", label: "その他" }
];

export default function ResourceProfileForm({ initialValues, onCompleted, onCancel, users, isEditing = false }: ResourceProfileFormProps) {
  const [state, setState] = useState<FormState>({
    values: initialValues ?? emptyProfile(),
    submitting: false,
    error: null
  });

  useEffect(() => {
    setState({ values: initialValues ?? emptyProfile(), submitting: false, error: null });
  }, [initialValues]);

  const updateValue = useCallback(<K extends keyof ResourceProfileFormValues>(key: K, value: ResourceProfileFormValues[K]) => {
    setState((prev) => ({ ...prev, values: { ...prev.values, [key]: value } }));
  }, []);

  const handleAddLink = () => {
    updateValue("links", [...(state.values.links ?? []), { service: SERVICE_OPTIONS[0].value, url: "" }]);
  };

  const handleLinkChange = (index: number, key: keyof ResourceLinkFormValues, value: unknown) => {
    const links = [...(state.values.links ?? [])];
    links[index] = { ...links[index], [key]: value } as ResourceLinkFormValues;
    updateValue("links", links);
  };

  const handleRemoveLink = (index: number) => {
    const links = [...(state.values.links ?? [])];
    links.splice(index, 1);
    updateValue("links", links);
  };

  const submit = async () => {
    setState((prev) => ({ ...prev, submitting: true, error: null }));
    try {
      const payload: ResourceProfileFormValues = {
        ...state.values,
        links: (state.values.links ?? []).filter((link) => link.url.trim().length)
      };

      if (!payload.user_id) {
        throw new Error("アカウントの選択が必要です");
      }

      const response = await fetch("/api/resources", {
        method: isEditing ? "PATCH" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.error ?? "保存に失敗しました");
      }

      onCompleted();
      setState({ values: emptyProfile(), submitting: false, error: null });
    } catch (error) {
      setState((prev) => ({
        ...prev,
        submitting: false,
        error: error instanceof Error ? error.message : "保存に失敗しました"
      }));
    }
  };
  return (
    <section className="rounded-lg border bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">{isEditing ? "リソースの編集" : "リソースの登録"}</h2>
          <p className="text-sm text-gray-600">社員アカウントと発信リンクを紐づけて共有しましょう。</p>
        </div>
        {isEditing && (
          <button
            type="button"
            onClick={() => {
              setState({ values: emptyProfile(), submitting: false, error: null });
              onCancel();
            }}
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100"
          >
            編集をキャンセル
          </button>
        )}
      </div>

      <div className="mt-4 flex flex-col">
        <label htmlFor="user" className="text-sm font-medium text-gray-700">
          アカウント <span className="text-red-500">*</span>
        </label>
        <select
          id="user"
          value={state.values.user_id}
          onChange={(event) => updateValue("user_id", event.target.value)}
          className="mt-1 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          disabled={isEditing}
        >
          <option value="">選択してください</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>
              {user.email}
            </option>
          ))}
        </select>
      </div>

      <div className="mt-6">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">リンク一覧</h3>
          <button
            type="button"
            onClick={handleAddLink}
            className="rounded-md border border-blue-200 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50"
          >
            リンクを追加
          </button>
        </div>

        <div className="mt-3 space-y-3">
          {(state.values.links ?? []).length === 0 ? (
            <p className="text-sm text-gray-500">まだリンクが登録されていません。</p>
          ) : (
            (state.values.links ?? []).map((link, index) => (
              <div key={link.id ?? index} className="rounded-md border border-gray-200 bg-gray-50 p-4">
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="flex flex-col">
                    <label className="text-xs font-medium text-gray-700">サービス</label>
                    <select
                      value={link.service}
                      onChange={(event) => handleLinkChange(index, "service", event.target.value)}
                      className="mt-1 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    >
                      {SERVICE_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex flex-col">
                    <label className="text-xs font-medium text-gray-700">URL</label>
                    <input
                      value={link.url}
                      onChange={(event) => handleLinkChange(index, "url", event.target.value)}
                      className="mt-1 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                      placeholder="https://example.com"
                    />
                  </div>
                </div>
                <div className="mt-3 flex justify-end">
                  <button
                    type="button"
                    onClick={() => handleRemoveLink(index)}
                    className="rounded-md border border-red-200 px-3 py-1.5 text-xs text-red-600 hover:bg-red-50"
                  >
                    削除
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {state.error && <p className="mt-4 text-sm text-red-600">{state.error}</p>}

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={submit}
          disabled={state.submitting}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {state.submitting ? "保存中..." : "リソースを保存"}
        </button>
        {!isEditing && (
          <button
            type="button"
            onClick={() => {
              setState({ values: emptyProfile(), submitting: false, error: null });
              onCancel();
            }}
            className="rounded-md border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-100"
          >
            クリア
          </button>
        )}
      </div>
    </section>
  );
}

