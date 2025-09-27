"use client";

import { ReactNode, useState } from "react";
import { Comment } from "@/lib/types/comments";
import CommentForm from "./CommentForm";
import { useUser } from "@supabase/auth-helpers-react";

interface CommentItemProps {
  comment: Comment;
  onReply: (content: string) => Promise<void> | void;
  onUpdate: (content: string) => Promise<void> | void;
  onDelete: () => Promise<void> | void;
  onReactionToggle: (emoji: string, hasReacted: boolean) => Promise<void> | void;
  children?: ReactNode;
}

const REACTION_EMOJIS = ["👍", "❤️", "😂", "😮", "😢", "😡"];

export default function CommentItem({
  comment,
  onReply,
  onUpdate,
  onDelete,
  onReactionToggle,
  children
}: CommentItemProps) {
  const [isReplying, setIsReplying] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(comment.content);
  const [isBusy, setIsBusy] = useState(false);
  const user = useUser();

  const handleUpdate = async () => {
    if (!editContent.trim()) return;

    try {
      setIsBusy(true);
      await onUpdate(editContent.trim());
      setIsEditing(false);
    } catch (error) {
      console.error("Error updating comment:", error);
      alert("コメントの更新に失敗しました");
    } finally {
      setIsBusy(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("このコメントを削除しますか？")) return;

    try {
      setIsBusy(true);
      await onDelete();
    } catch (error) {
      console.error("Error deleting comment:", error);
      alert("コメントの削除に失敗しました");
    } finally {
      setIsBusy(false);
    }
  };

  const handleReactionClick = async (emoji: string) => {
    const userId = user?.id;
    const users = comment.reactions[emoji] || [];
    const hasReacted = userId ? users.includes(userId) : false;

    try {
      setIsBusy(true);
      await onReactionToggle(emoji, hasReacted);
    } catch (error) {
      console.error("Error toggling reaction:", error);
    } finally {
      setIsBusy(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("ja-JP");
  };

  const displayAuthor = comment.author?.name || comment.author?.email || comment.author_id;

  return (
    <div className="border-l-2 border-gray-200 pl-4">
      <div className="bg-white rounded-lg p-4 shadow-sm">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-medium text-sm">{displayAuthor}</span>
              <span className="text-xs text-gray-500">
                {formatDate(comment.created_at)}
              </span>
              {comment.updated_at !== comment.created_at && (
                <span className="text-xs text-gray-400">(編集済み)</span>
              )}
            </div>

            {isEditing ? (
              <div className="space-y-2">
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  className="w-full p-2 border rounded-md resize-none"
                  rows={3}
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleUpdate}
                    disabled={isBusy || !editContent.trim()}
                    className="px-3 py-1 bg-blue-500 text-white rounded text-sm disabled:opacity-50"
                  >
                    {isBusy ? "更新中..." : "更新"}
                  </button>
                  <button
                    onClick={() => {
                      setIsEditing(false);
                      setEditContent(comment.content);
                    }}
                    className="px-3 py-1 bg-gray-500 text-white rounded text-sm"
                  >
                    キャンセル
                  </button>
                </div>
              </div>
            ) : (
              <div className="prose prose-sm max-w-none">
                <p className="whitespace-pre-wrap">{comment.content}</p>
              </div>
            )}
          </div>

          <div className="flex gap-1 ml-2">
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="text-xs text-gray-500 hover:text-gray-700"
            >
              編集
            </button>
            <button
              onClick={handleDelete}
              className="text-xs text-red-500 hover:text-red-700"
            >
              削除
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2 mt-3">
          {REACTION_EMOJIS.map((emoji) => {
            const userId = user?.id;
            const users = comment.reactions[emoji] || [];
            const hasReacted = userId ? users.includes(userId) : false;
            return (
              <button
                key={emoji}
                onClick={() => handleReactionClick(emoji)}
                disabled={isBusy}
                className={`flex items-center gap-1 px-2 py-1 rounded-full text-sm transition-colors ${
                  hasReacted
                    ? "bg-blue-100 text-blue-700"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                } ${isBusy ? "opacity-60 cursor-not-allowed" : ""}`}
              >
                <span>{emoji}</span>
                {users.length > 0 && <span>{users.length}</span>}
              </button>
            );
          })}
        </div>

        <div className="mt-3">
          <button
            onClick={() => setIsReplying(!isReplying)}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            {isReplying ? "返信をキャンセル" : "返信"}
          </button>
        </div>

        {isReplying && (
          <div className="mt-3">
            <CommentForm
              onSubmit={async (content) => {
                await onReply(content);
                setIsReplying(false);
              }}
              isLoading={isBusy}
              placeholder="返信を入力..."
            />
          </div>
        )}
      </div>

      {children && <div className="mt-4 space-y-4">{children}</div>}
    </div>
  );
}
