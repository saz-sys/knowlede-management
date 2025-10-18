"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

interface DeleteButtonProps {
  postId: string;
  postTitle: string;
  authorId: string;
  currentUserId: string;
}

export default function DeleteButton({ postId, postTitle, authorId, currentUserId }: DeleteButtonProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const router = useRouter();

  // 投稿の所有者でない場合は表示しない
  if (authorId !== currentUserId) {
    return null;
  }

  const handleDelete = async () => {
    setIsDeleting(true);
    
    try {
      const response = await fetch(`/api/posts/${postId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const data = await response.json();
        
        if (data.error === "HAS_RELATED_DATA") {
          // 関連データがある場合は強制削除を確認
          const forceDelete = confirm(
            `この投稿には関連するデータがあります（コメント: ${data.details.comments}件、ブックマーク: ${data.details.bookmarks}件）。\n\n強制的に削除しますか？`
          );
          
          if (forceDelete) {
            const forceResponse = await fetch(`/api/posts/${postId}`, {
              method: "DELETE",
              headers: {
                "Content-Type": "application/json",
                "X-Force-Delete": "true",
              },
            });
            
            if (!forceResponse.ok) {
              throw new Error("削除に失敗しました");
            }
          } else {
            setIsDeleting(false);
            setShowConfirm(false);
            return;
          }
        } else {
          throw new Error(data.error || "削除に失敗しました");
        }
      }

      // 削除成功
      router.push("/");
    } catch (error) {
      console.error("Delete error:", error);
      alert("削除に失敗しました: " + (error as Error).message);
    } finally {
      setIsDeleting(false);
      setShowConfirm(false);
    }
  };

  if (showConfirm) {
    return (
      <div className="flex items-center gap-2">
        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="rounded bg-red-600 px-3 py-1 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
        >
          {isDeleting ? "削除中..." : "削除確認"}
        </button>
        <button
          onClick={() => setShowConfirm(false)}
          disabled={isDeleting}
          className="rounded bg-gray-300 px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-400"
        >
          キャンセル
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={() => setShowConfirm(true)}
      className="rounded bg-red-600 px-3 py-1 text-sm font-medium text-white hover:bg-red-700"
    >
      削除
    </button>
  );
}
