-- Ensure posts and comments reference auth.users for PostgREST relationships
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'posts_author_id_fkey'
      AND conrelid = 'public.posts'::regclass
  ) THEN
    ALTER TABLE public.posts
      ADD CONSTRAINT posts_author_id_fkey
      FOREIGN KEY (author_id)
      REFERENCES auth.users (id)
      ON DELETE CASCADE;
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'comments_author_id_fkey'
      AND conrelid = 'public.comments'::regclass
  ) THEN
    ALTER TABLE public.comments
      ADD CONSTRAINT comments_author_id_fkey
      FOREIGN KEY (author_id)
      REFERENCES auth.users (id)
      ON DELETE CASCADE;
  END IF;
END
$$;

-- migration revision timestamp 20250927-02

