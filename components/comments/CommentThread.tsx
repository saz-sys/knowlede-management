"use client";

import { useState, useEffect, useCallback } from "react";
import { Comment } from "@/lib/types/comments";
import CommentItem from "./CommentItem";
import CommentForm from "./CommentForm";

interface CommentThreadProps {
  postId: string;
  initialComments: Comment[];
}

export default function CommentThread({ postId, initialComments }: CommentThreadProps) {
  const [comments, setComments] = useState<Comment[]>(initialComments);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchComments = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const response = await fetch(`/api/comments?post_id=${postId}`);
      if (!response.ok) {
        throw new Error("Failed to fetch comments");
      }
      const { comments: fetched } = await response.json();
      setComments(fetched ?? []);
    } catch (error) {
      console.error("Error fetching comments:", error);
    } finally {
      setIsRefreshing(false);
    }
  }, [postId]);

  useEffect(() => {
    setComments(initialComments);
  }, [initialComments]);

  const handleCommentSubmit = async (content: string, parentId?: string) => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/comments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          post_id: postId,
          parent_id: parentId,
          content
        })
      });

      if (!response.ok) {
        throw new Error("Failed to create comment");
      }

      await fetchComments();
    } catch (error) {
      console.error("Error creating comment:", error);
      alert("コメントの作成に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCommentUpdate = async (commentId: string, content: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/comments/${commentId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ content })
      });

      if (!response.ok) {
        throw new Error("Failed to update comment");
      }

      await fetchComments();
    } catch (error) {
      console.error("Error updating comment:", error);
      alert("コメントの更新に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCommentDelete = async (commentId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/comments/${commentId}`, {
        method: "DELETE"
      });

      if (!response.ok) {
        throw new Error("Failed to delete comment");
      }

      await fetchComments();
    } catch (error) {
      console.error("Error deleting comment:", error);
      alert("コメントの削除に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReactionToggle = async (commentId: string, emoji: string, hasReacted: boolean) => {
    try {
      const response = await fetch(`/api/comments/${commentId}/reactions`, {
        method: hasReacted ? "DELETE" : "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ emoji })
      });

      if (!response.ok) {
        throw new Error("Failed to toggle reaction");
      }

      await fetchComments();
    } catch (error) {
      console.error("Error toggling reaction:", error);
    }
  };

  const renderComment = (comment: Comment) => (
    <CommentItem
      key={comment.id}
      comment={comment}
      onReply={(content) => handleCommentSubmit(content, comment.id)}
      onUpdate={(content) => handleCommentUpdate(comment.id, content)}
      onDelete={() => handleCommentDelete(comment.id)}
      onReactionToggle={(emoji, hasReacted) => handleReactionToggle(comment.id, emoji, hasReacted)}
    >
      {comment.replies?.map((reply) => renderComment(reply))}
    </CommentItem>
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <h3 className="text-lg font-semibold">コメント</h3>
        {isRefreshing && <span className="text-sm text-gray-400">更新中...</span>}
      </div>

      <CommentForm
        onSubmit={(content) => handleCommentSubmit(content)}
        isLoading={isLoading}
        placeholder="コメントを追加..."
      />

      <div className="space-y-4">
        {comments.map((comment) => renderComment(comment))}
      </div>

      {comments.length === 0 && !isRefreshing && (
        <p className="text-gray-500 text-center py-4">
          まだコメントがありません。最初のコメントを投稿してみましょう！
        </p>
      )}
    </div>
  );
}
