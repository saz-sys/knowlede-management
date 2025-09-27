-- Track HTTP cache validators for RSS feeds
ALTER TABLE public.rss_feeds
  ADD COLUMN IF NOT EXISTS last_etag text,
  ADD COLUMN IF NOT EXISTS last_modified text;
