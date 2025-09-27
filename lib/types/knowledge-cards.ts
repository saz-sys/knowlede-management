export interface KnowledgeCard {
  id: string;
  post_id: string;
  title: string;
  content: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  created_by_user?: {
    id: string;
    email: string;
    name?: string;
  };
  related_comment_ids?: string[];
}

export interface CreateKnowledgeCardRequest {
  post_id: string;
  title: string;
  content: string;
  related_comment_ids?: string[];
}

export interface UpdateKnowledgeCardRequest {
  title: string;
  content: string;
  related_comment_ids?: string[];
}
