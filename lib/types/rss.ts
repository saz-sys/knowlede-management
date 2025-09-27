export interface RssFeed {
  id: string;
  name: string;
  url: string;
  tags: string[] | null;
  is_active: boolean;
  last_fetched_at: string | null;
  created_at: string | null;
}

