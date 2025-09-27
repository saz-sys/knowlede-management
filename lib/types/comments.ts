export interface Comment {
  id: string;
  post_id: string;
  author_id: string;
  parent_id?: string;
  content: string;
  reactions: Record<string, string[]>; // emoji -> user_ids
  created_at: string;
  updated_at: string;
  author?: {
    id: string;
    email: string;
    name?: string;
  };
  replies?: Comment[];
  reply_count?: number;
}

export interface CreateCommentRequest {
  post_id: string;
  parent_id?: string;
  content: string;
}

export interface UpdateCommentRequest {
  content: string;
}

export interface AddReactionRequest {
  emoji: string;
}

export interface RemoveReactionRequest {
  emoji: string;
}

export interface CommentReaction {
  emoji: string;
  user_id: string;
  created_at: string;
}
