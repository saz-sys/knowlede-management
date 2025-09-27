export interface Post {
  id: string;
  author_id: string;
  author_email?: string | null;
  title: string;
  url: string;
  content?: string;
  summary?: string;
  notified_channels?: string[];
  metadata?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
  author?: {
    id: string;
    email: string;
    name?: string;
  };
}

export interface CreatePostRequest {
  title: string;
  url: string;
  content?: string;
  summary?: string;
  notified_channels?: string[];
  tags?: string[];
}

